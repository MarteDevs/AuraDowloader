package com.mars.auraapp.util

import android.app.DownloadManager
import android.content.Context
import android.net.Uri
import android.os.Environment
import com.mars.auraapp.BuildConfig
import com.mars.auraapp.data.storage.TokenStore
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Wrapper around Android's DownloadManager. Downloads the audio file for a
 * completed server-side download to the device's public Music/Aura folder.
 * The token is passed as ?token=… because the backend's serve_file endpoint
 * accepts either Bearer header or query string (the latter is mandatory
 * because Android's DownloadManager cannot send custom headers).
 */
@Singleton
class FileDownloader @Inject constructor(
    @ApplicationContext private val context: Context,
    private val tokenStore: TokenStore,
) {
    fun enqueue(downloadId: String, fileName: String): Long {
        val token = tokenStore.get().orEmpty()
        val url = if (token.isBlank()) {
            "${BuildConfig.BACKEND_BASE_URL}download/file/$downloadId"
        } else {
            "${BuildConfig.BACKEND_BASE_URL}download/file/$downloadId?token=" +
                java.net.URLEncoder.encode(token, "UTF-8")
        }
        val safeName = fileName.ifBlank { "aura_track_$downloadId" }
            .replace(Regex("[^A-Za-z0-9._-]"), "_")

        val request = DownloadManager.Request(Uri.parse(url))
            .setTitle(safeName)
            .setDescription("Aura Music")
            .setMimeType("audio/mpeg")
            .setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
            .setAllowedOverMetered(true)
            .setAllowedOverRoaming(true)
            .setDestinationInExternalPublicDir(Environment.DIRECTORY_MUSIC, "Aura/$safeName")

        val dm = context.getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
        return dm.enqueue(request)
    }
}
