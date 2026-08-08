package com.mars.auraapp.data.api

import com.mars.auraapp.data.api.dto.AlbumDownloadRequest
import com.mars.auraapp.data.api.dto.AlbumDownloadResponse
import com.mars.auraapp.data.api.dto.DownloadRequest
import com.mars.auraapp.data.api.dto.DownloadResponse
import com.mars.auraapp.data.api.dto.GenericResponse
import com.mars.auraapp.data.api.dto.QueueResponse
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

interface DownloadApi {
    @POST("download")
    suspend fun startDownload(@Body body: DownloadRequest): DownloadResponse

    @POST("download/album")
    suspend fun startAlbumDownload(@Body body: AlbumDownloadRequest): AlbumDownloadResponse

    @GET("download/queue")
    suspend fun getQueue(): QueueResponse

    @POST("download/cancel/{id}")
    suspend fun cancel(@Path("id") downloadId: String): GenericResponse

    @POST("download/retry/{id}")
    suspend fun retry(@Path("id") downloadId: String): DownloadResponse

    @DELETE("download/{id}")
    suspend fun remove(@Path("id") downloadId: String): GenericResponse
}
