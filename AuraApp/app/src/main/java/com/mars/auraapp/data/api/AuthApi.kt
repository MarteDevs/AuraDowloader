package com.mars.auraapp.data.api

import com.mars.auraapp.data.api.dto.AuthStatusResponse
import com.mars.auraapp.data.api.dto.LoginRequest
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface AuthApi {
    @GET("auth/status")
    suspend fun status(): AuthStatusResponse

    @POST("auth/login")
    suspend fun login(@Body body: LoginRequest): Response<Unit>
}
