package com.mars.auraapp.data.api

import retrofit2.http.GET

interface HealthApi {
    @GET("health")
    suspend fun health(): Map<String, String>
}
