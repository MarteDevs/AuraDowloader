package com.mars.auraapp.data.storage

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.mars.auraapp.data.api.dto.DownloadItem
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import kotlinx.serialization.builtins.ListSerializer
import kotlinx.serialization.json.Json
import javax.inject.Inject
import javax.inject.Singleton

private val Context.queueDataStore by preferencesDataStore(name = "aura_queue_cache")

@Singleton
class QueueCache @Inject constructor(
    @ApplicationContext private val context: Context,
    private val json: Json,
) {
    private val key = stringPreferencesKey("last_queue_json")

    val lastQueue: Flow<List<DownloadItem>> = context.queueDataStore.data.map { prefs ->
        val raw = prefs[key] ?: return@map emptyList()
        runCatching {
            json.decodeFromString(ListSerializer(DownloadItem.serializer()), raw)
        }.getOrDefault(emptyList())
    }

    suspend fun save(items: List<DownloadItem>) {
        val raw = json.encodeToString(ListSerializer(DownloadItem.serializer()), items)
        context.queueDataStore.edit { it[key] = raw }
    }
}
