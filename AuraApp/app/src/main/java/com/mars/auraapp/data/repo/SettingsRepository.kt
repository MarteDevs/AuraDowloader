package com.mars.auraapp.data.repo

import com.mars.auraapp.data.api.SettingsApi
import com.mars.auraapp.data.api.dto.PublicSettings
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SettingsRepository @Inject constructor(
    private val settingsApi: SettingsApi,
) {
    suspend fun get(): PublicSettings = settingsApi.get()

    suspend fun save(settings: PublicSettings): PublicSettings = settingsApi.save(settings).settings
}
