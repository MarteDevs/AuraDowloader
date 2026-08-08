package com.mars.auraapp.ui.queue

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.mars.auraapp.data.api.dto.DownloadItem
import com.mars.auraapp.data.repo.DownloadRepository
import com.mars.auraapp.data.storage.QueueCache
import com.mars.auraapp.data.ws.DownloadEvent
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class QueueUiState(
    val items: List<DownloadItem> = emptyList(),
    val loading: Boolean = false,
    val connected: Boolean = false,
    val error: String? = null,
)

@HiltViewModel
class DownloadQueueViewModel @Inject constructor(
    private val downloadRepository: DownloadRepository,
    private val queueCache: QueueCache,
) : ViewModel() {

    private val _state = MutableStateFlow(QueueUiState())
    val state: StateFlow<QueueUiState> = _state.asStateFlow()

    init {
        // Hydrate from offline cache first.
        viewModelScope.launch {
            queueCache.lastQueue.collect { cached ->
                if (cached.isNotEmpty() && _state.value.items.isEmpty()) {
                    _state.update { it.copy(items = cached) }
                }
            }
        }
        refresh()
        observeEvents()
    }

    fun refresh() {
        viewModelScope.launch {
            _state.update { it.copy(loading = true) }
            runCatching { downloadRepository.getQueue() }
                .onSuccess { items ->
                    _state.update { it.copy(loading = false, items = items, error = null) }
                    queueCache.save(items)
                }
                .onFailure { err ->
                    _state.update { it.copy(loading = false, error = err.message ?: "Error") }
                }
        }
    }

    private fun observeEvents() {
        viewModelScope.launch {
            downloadRepository.events.collect { event ->
                when (event) {
                    DownloadEvent.Connected -> _state.update { it.copy(connected = true) }
                    DownloadEvent.Disconnected -> _state.update { it.copy(connected = false) }
                    is DownloadEvent.Queued -> upsertItem(event.item)
                    is DownloadEvent.Progress -> upsertItem(event.item)
                    is DownloadEvent.Completed -> upsertItem(event.item)
                    is DownloadEvent.Error -> upsertItem(event.item)
                    is DownloadEvent.Cancelled -> upsertItem(event.item)
                }
                // Persist on every change so the cache survives process death.
                queueCache.save(_state.value.items)
            }
        }
    }

    private fun upsertItem(newItem: DownloadItem) {
        _state.update { current ->
            val newList = current.items.toMutableList()
            val idx = newList.indexOfFirst { it.id == newItem.id }
            if (idx >= 0) newList[idx] = newItem else newList.add(0, newItem)
            current.copy(items = newList)
        }
    }

    fun cancel(id: String) {
        viewModelScope.launch { downloadRepository.cancel(id) }
    }

    fun retry(id: String) {
        viewModelScope.launch { downloadRepository.retry(id) }
    }

    fun remove(id: String) {
        viewModelScope.launch { downloadRepository.remove(id) }
    }

    fun clearError() {
        _state.update { it.copy(error = null) }
    }
}
