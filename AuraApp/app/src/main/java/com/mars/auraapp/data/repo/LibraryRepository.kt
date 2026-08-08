package com.mars.auraapp.data.repo

import com.mars.auraapp.data.api.LibraryApi
import com.mars.auraapp.data.api.dto.TrackDto
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class LibraryRepository @Inject constructor(
    private val libraryApi: LibraryApi,
) {
    suspend fun library(): List<TrackDto> = libraryApi.library().tracks

    suspend fun favorites(): List<TrackDto> = libraryApi.favorites().tracks

    suspend fun toggleFavorite(trackId: String): Boolean =
        runCatching { libraryApi.toggleFavorite(trackId).is_favorite }.getOrDefault(false)
}
