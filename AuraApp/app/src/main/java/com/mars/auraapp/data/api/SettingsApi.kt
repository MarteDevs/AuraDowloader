package com.mars.auraapp.data.api

import com.mars.auraapp.data.api.dto.PublicSettings
import com.mars.auraapp.data.api.dto.SettingsEnvelope
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface SettingsApi {
    @GET("settings")
    suspend fun get(): PublicSettings

    @POST("settings")
    suspend fun save(@Body body: PublicSettings): SettingsEnvelope
}
