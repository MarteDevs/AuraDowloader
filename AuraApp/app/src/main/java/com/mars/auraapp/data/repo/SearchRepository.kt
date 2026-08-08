package com.mars.auraapp.data.repo

import com.mars.auraapp.data.api.SearchApi
import com.mars.auraapp.data.api.dto.Album
import com.mars.auraapp.data.api.dto.AlbumTracksResponse
import com.mars.auraapp.data.api.dto.Track
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SearchRepository @Inject constructor(
    private val searchApi: SearchApi,
) {
    suspend fun searchTracks(query: String, engine: String = "youtube", limit: Int = 15): List<Track> =
        searchApi.search(query, engine, limit).results

    suspend fun searchAlbums(query: String, engine: String = "youtube", limit: Int = 15): List<Album> =
        searchApi.searchAlbums(query, engine, limit).results

    suspend fun albumTracks(albumId: String, engine: String = "youtube"): AlbumTracksResponse =
        searchApi.albumTracks(albumId, engine)
}
