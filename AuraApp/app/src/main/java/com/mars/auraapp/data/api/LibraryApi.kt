package com.mars.auraapp.data.api

import com.mars.auraapp.data.api.dto.FavoriteToggleResponse
import com.mars.auraapp.data.api.dto.LibraryResponse
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

interface LibraryApi {
    @GET("library")
    suspend fun library(): LibraryResponse

    @GET("favorites")
    suspend fun favorites(): LibraryResponse

    @POST("favorites/{id}/toggle")
    suspend fun toggleFavorite(@Path("id") trackId: String): FavoriteToggleResponse
}
