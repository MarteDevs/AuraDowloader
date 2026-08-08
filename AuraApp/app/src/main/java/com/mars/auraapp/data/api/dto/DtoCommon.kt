package com.mars.auraapp.data.api.dto

import kotlinx.serialization.Serializable

@Serializable
data class AuthStatusResponse(
    val auth_required: Boolean,
    val version: String = "",
)

@Serializable
data class LoginRequest(
    val token: String,
)
