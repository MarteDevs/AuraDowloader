package com.mars.auraapp.data.api.dto

import kotlinx.serialization.Serializable

@Serializable
data class Track(
    val id: String,
    val title: String,
    val artist: String,
    val thumbnail: String = "",
    val duration: String? = null,
    val duration_sec: Int = 0,
    val url: String = "",
    val engine: String = "youtube",
    val album: String? = null,
)

@Serializable
data class Album(
    val id: String,
    val title: String,
    val artist: String,
    val thumbnail: String = "",
    val engine: String = "youtube",
    val track_count: Int = 0,
)

@Serializable
data class SearchResponse<T>(
    val query: String,
    val engine: String,
    val count: Int,
    val results: List<T> = emptyList(),
)

@Serializable
data class AlbumTracksResponse(
    val album_id: String,
    val engine: String,
    val count: Int,
    val tracks: List<Track> = emptyList(),
)
