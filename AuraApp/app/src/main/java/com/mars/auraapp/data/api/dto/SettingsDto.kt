package com.mars.auraapp.data.api.dto

import kotlinx.serialization.Serializable

@Serializable
data class PublicSettings(
    val has_arl: Boolean,
    val default_quality: String,
    val download_dir: String,
    val cookies_file: String,
)

@Serializable
data class SettingsEnvelope(
    val status: String,
    val settings: PublicSettings,
)
