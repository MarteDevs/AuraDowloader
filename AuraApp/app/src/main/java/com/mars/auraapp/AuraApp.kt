package com.mars.auraapp

import android.app.Application
import com.mars.auraapp.data.ws.DownloadSocket
import dagger.hilt.android.HiltAndroidApp
import javax.inject.Inject

@HiltAndroidApp
class AuraApp : Application() {

    @Inject
    lateinit var downloadSocket: DownloadSocket

    override fun onCreate() {
        super.onCreate()
        // Open the WebSocket as soon as the process is alive. The socket reads
        // the current token from TokenStore on each connect/reconnect; if the
        // user is not authenticated the server will close with 1008 and the
        // client will stop reconnecting (see DownloadSocket.onClosed).
        downloadSocket.connect()
    }

    override fun onTerminate() {
        downloadSocket.shutdown()
        super.onTerminate()
    }
}
