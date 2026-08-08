package com.mars.auraapp.data.ws

import com.mars.auraapp.data.api.dto.DownloadItem
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class WsEnvelope(
    val type: String,
    val item: DownloadItem? = null,
)

sealed interface DownloadEvent {
    data class Queued(val item: DownloadItem) : DownloadEvent
    data class Progress(val item: DownloadItem) : DownloadEvent
    data class Completed(val item: DownloadItem) : DownloadEvent
    data class Error(val item: DownloadItem) : DownloadEvent
    data class Cancelled(val item: DownloadItem) : DownloadEvent
    data object Connected : DownloadEvent
    data object Disconnected : DownloadEvent
}

internal fun WsEnvelope.toEvent(): DownloadEvent? {
    val it = item ?: return null
    return when (type) {
        "download_queued" -> DownloadEvent.Queued(it)
        "download_progress" -> DownloadEvent.Progress(it)
        "download_completed" -> DownloadEvent.Completed(it)
        "download_error" -> DownloadEvent.Error(it)
        "download_cancelled" -> DownloadEvent.Cancelled(it)
        else -> null
    }
}
