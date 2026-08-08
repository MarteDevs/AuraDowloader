package com.mars.auraapp.data.api.dto

import kotlinx.serialization.Serializable

@Serializable
data class TrackDto(
    val id: String,
    val title: String,
    val artist: String,
    val album: String? = null,
    val thumbnail: String = "",
    val duration: String? = null,
    val duration_sec: Int = 0,
    val file_path: String = "",
    val file_name: String = "",
    val quality: String = "320k",
    val engine: String = "youtube",
    val is_favorite: Boolean = false,
    val created_at: String? = null,
)

@Serializable
data class LibraryResponse(
    val count: Int,
    val tracks: List<TrackDto> = emptyList(),
)

@Serializable
data class FavoriteToggleResponse(
    val status: String,
    val track_id: String,
    val is_favorite: Boolean,
)
