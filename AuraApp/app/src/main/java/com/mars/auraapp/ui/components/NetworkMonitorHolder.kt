package com.mars.auraapp.ui.components

import androidx.lifecycle.ViewModel
import com.mars.auraapp.util.NetworkMonitor
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject

@HiltViewModel
class NetworkMonitorHolder @Inject constructor(
    val monitor: NetworkMonitor,
) : ViewModel()
