package com.mars.auraapp.ui.search

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.mars.auraapp.data.api.dto.Album
import com.mars.auraapp.data.api.dto.DownloadRequest
import com.mars.auraapp.data.api.dto.Track
import com.mars.auraapp.data.repo.DownloadRepository
import com.mars.auraapp.data.repo.SearchRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

enum class SearchTab { TRACKS, ALBUMS }

data class SearchUiState(
    val tab: SearchTab = SearchTab.TRACKS,
    val query: String = "",
    val engine: String = "youtube",
    val loading: Boolean = false,
    val error: String? = null,
    val tracks: List<Track> = emptyList(),
    val albums: List<Album> = emptyList(),
    val downloadingTrackId: String? = null,
)

@HiltViewModel
class SearchViewModel @Inject constructor(
    private val searchRepository: SearchRepository,
    private val downloadRepository: DownloadRepository,
) : ViewModel() {

    private val _state = MutableStateFlow(SearchUiState())
    val state: StateFlow<SearchUiState> = _state.asStateFlow()

    private var searchJob: Job? = null

    fun onTabChange(tab: SearchTab) {
        _state.update { it.copy(tab = tab) }
    }

    fun onQueryChange(query: String) {
        _state.update { it.copy(query = query) }
    }

    fun onEngineChange(engine: String) {
        _state.update { it.copy(engine = engine) }
        if (_state.value.query.isNotBlank()) performSearch()
    }

    fun performSearch() {
        val current = _state.value
        if (current.query.isBlank()) return
        searchJob?.cancel()
        searchJob = viewModelScope.launch {
            _state.update { it.copy(loading = true, error = null) }
            delay(300) // Debounce
            val result = runCatching {
                when (current.tab) {
                    SearchTab.TRACKS -> searchRepository.searchTracks(current.query, current.engine)
                    SearchTab.ALBUMS -> searchRepository.searchAlbums(current.query, current.engine)
                }
            }
            result.onSuccess { data ->
                val (tracks, albums) = when (current.tab) {
                    SearchTab.TRACKS -> @Suppress("UNCHECKED_CAST") (data as List<Track>) to emptyList()
                    SearchTab.ALBUMS -> emptyList<Track>() to @Suppress("UNCHECKED_CAST") (data as List<Album>)
                }
                _state.update {
                    it.copy(loading = false, tracks = tracks, albums = albums, error = null)
                }
            }.onFailure { err ->
                _state.update { it.copy(loading = false, error = err.message ?: "Error de búsqueda") }
            }
        }
    }

    fun startDownload(track: Track, quality: String = "320k") {
        viewModelScope.launch {
            _state.update { it.copy(downloadingTrackId = track.id) }
            val req = DownloadRequest(
                id = track.id,
                title = track.title,
                artist = track.artist,
                thumbnail = track.thumbnail,
                url = track.url,
                engine = track.engine,
                quality = quality,
            )
            runCatching { downloadRepository.startDownload(req) }
                .onSuccess { _state.update { it.copy(downloadingTrackId = null) } }
                .onFailure { err ->
                    _state.update {
                        it.copy(downloadingTrackId = null, error = err.message ?: "No se pudo encolar")
                    }
                }
        }
    }

    fun clearError() {
        _state.update { it.copy(error = null) }
    }
}
