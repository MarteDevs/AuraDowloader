package com.mars.auraapp.data.api

import com.mars.auraapp.data.api.dto.Album
import com.mars.auraapp.data.api.dto.AlbumTracksResponse
import com.mars.auraapp.data.api.dto.SearchResponse
import com.mars.auraapp.data.api.dto.Track
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

interface SearchApi {
    @GET("search")
    suspend fun search(
        @Query("q") query: String,
        @Query("engine") engine: String = "youtube",
        @Query("limit") limit: Int = 15,
    ): SearchResponse<Track>

    @GET("search/albums")
    suspend fun searchAlbums(
        @Query("q") query: String,
        @Query("engine") engine: String = "youtube",
        @Query("limit") limit: Int = 15,
    ): SearchResponse<Album>

    @GET("album/{id}/tracks")
    suspend fun albumTracks(
        @Path("id") albumId: String,
        @Query("engine") engine: String = "youtube",
    ): AlbumTracksResponse
}
