package com.mars.auraapp.data.api.dto

import kotlinx.serialization.Serializable

@Serializable
data class DownloadItem(
    val id: String,
    val title: String,
    val artist: String,
    val thumbnail: String = "",
    val engine: String = "youtube",
    val quality: String = "320k",
    val status: String,
    val progress: Double = 0.0,
    val speed: String = "",
    val eta: String = "",
    val file_name: String = "",
    val file_path: String = "",
    val error_message: String = "",
    val created_at: Double = 0.0,
)

@Serializable
data class DownloadRequest(
    val id: String,
    val title: String,
    val artist: String,
    val thumbnail: String = "",
    val url: String = "",
    val engine: String = "youtube",
    val quality: String = "320k",
)

@Serializable
data class DownloadResponse(
    val status: String,
    val download_id: String? = null,
    val item: DownloadItem? = null,
)

@Serializable
data class AlbumDownloadRequest(
    val album_id: String,
    val album_title: String,
    val artist: String,
    val engine: String = "youtube",
    val quality: String = "320k",
    val tracks: List<DownloadRequest>,
)

@Serializable
data class AlbumDownloadResponse(
    val status: String,
    val album_title: String,
    val total_tracks: Int,
    val items: List<DownloadItem> = emptyList(),
)

@Serializable
data class QueueResponse(
    val count: Int,
    val items: List<DownloadItem> = emptyList(),
)

@Serializable
data class GenericResponse(
    val status: String,
    val download_id: String? = null,
    val item: DownloadItem? = null,
)
