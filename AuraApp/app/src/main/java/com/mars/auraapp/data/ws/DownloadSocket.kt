package com.mars.auraapp.data.ws

import com.mars.auraapp.BuildConfig
import com.mars.auraapp.data.storage.TokenStore
import com.mars.auraapp.di.WsClient
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.launch
import kotlinx.serialization.json.Json
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class DownloadSocket @Inject constructor(
    @WsClient private val client: OkHttpClient,
    private val tokenStore: TokenStore,
    private val json: Json,
) {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val _events = MutableSharedFlow<DownloadEvent>(replay = 0, extraBufferCapacity = 64)
    val events: SharedFlow<DownloadEvent> = _events.asSharedFlow()

    private var ws: WebSocket? = null
    private var pingJob: Job? = null
    private var reconnectJob: Job? = null
    private var isClosedManually = false
    private var reconnectDelay = 1_000L
    private val maxReconnectDelay = 30_000L

    fun connect() {
        if (ws != null) return
        isClosedManually = false
        val token = tokenStore.get().orEmpty()
        val url = if (token.isBlank()) BuildConfig.WS_BASE_URL
                  else "${BuildConfig.WS_BASE_URL}?token=${java.net.URLEncoder.encode(token, "UTF-8")}"
        val request = Request.Builder().url(url).build()
        ws = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                reconnectDelay = 1_000L
                _events.tryEmit(DownloadEvent.Connected)
                startPingLoop()
            }
            override fun onMessage(webSocket: WebSocket, text: String) {
                val envelope = runCatching { json.decodeFromString(WsEnvelope.serializer(), text) }.getOrNull()
                envelope?.toEvent()?.let { _events.tryEmit(it) }
            }
            override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
                webSocket.close(1000, null)
            }
            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                cleanupSocket()
                _events.tryEmit(DownloadEvent.Disconnected)
                if (code == 1008) {
                    // 1008 = policy violation → token rejected, do not reconnect
                    isClosedManually = true
                    return
                }
                if (!isClosedManually) scheduleReconnect()
            }
            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                cleanupSocket()
                _events.tryEmit(DownloadEvent.Disconnected)
                if (!isClosedManually) scheduleReconnect()
            }
        })
    }

    fun close() {
        isClosedManually = true
        reconnectJob?.cancel()
        pingJob?.cancel()
        ws?.close(1000, "client closed")
        ws = null
    }

    private fun startPingLoop() {
        pingJob?.cancel()
        pingJob = scope.launch {
            while (ws != null) {
                delay(25_000L)
                ws?.send("ping")
            }
        }
    }

    private fun scheduleReconnect() {
        if (isClosedManually || reconnectJob != null) return
        val delayMs = reconnectDelay
        reconnectJob = scope.launch {
            delay(delayMs)
            reconnectJob = null
            if (!isClosedManually) connect()
        }
        reconnectDelay = (reconnectDelay * 2).coerceAtMost(maxReconnectDelay)
    }

    private fun cleanupSocket() {
        pingJob?.cancel()
        pingJob = null
        ws = null
    }

    /** Cleanup global. Llamar desde AuraApp.onTerminate si se necesita. */
    fun shutdown() {
        close()
        scope.cancel()
    }
}
