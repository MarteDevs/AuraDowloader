package com.mars.auraapp.data.repo

import com.mars.auraapp.data.api.DownloadApi
import com.mars.auraapp.data.api.dto.AlbumDownloadRequest
import com.mars.auraapp.data.api.dto.DownloadItem
import com.mars.auraapp.data.api.dto.DownloadRequest
import com.mars.auraapp.data.ws.DownloadEvent
import com.mars.auraapp.data.ws.DownloadSocket
import kotlinx.coroutines.flow.SharedFlow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class DownloadRepository @Inject constructor(
    private val downloadApi: DownloadApi,
    private val downloadSocket: DownloadSocket,
) {
    /** Live updates from the WebSocket feed. */
    val events: SharedFlow<DownloadEvent> = downloadSocket.events

    suspend fun startDownload(track: DownloadRequest): DownloadItem? =
        downloadApi.startDownload(track).item

    suspend fun startAlbumDownload(album: AlbumDownloadRequest): List<DownloadItem> =
        downloadApi.startAlbumDownload(album).items

    suspend fun getQueue(): List<DownloadItem> =
        downloadApi.getQueue().items

    suspend fun cancel(downloadId: String): Boolean =
        runCatching { downloadApi.cancel(downloadId) }.isSuccess

    suspend fun retry(downloadId: String): DownloadItem? =
        downloadApi.retry(downloadId).item

    suspend fun remove(downloadId: String): Boolean =
        runCatching { downloadApi.remove(downloadId) }.isSuccess
}
