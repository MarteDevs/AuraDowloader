package com.mars.auraapp.ui.library

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.mars.auraapp.data.api.dto.TrackDto
import com.mars.auraapp.data.repo.LibraryRepository
import com.mars.auraapp.util.FileDownloader
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class FavoritesUiState(
    val tracks: List<TrackDto> = emptyList(),
    val loading: Boolean = false,
    val error: String? = null,
    val downloadInProgress: String? = null,
)

@HiltViewModel
class FavoritesViewModel @Inject constructor(
    private val libraryRepository: LibraryRepository,
    private val fileDownloader: FileDownloader,
) : ViewModel() {

    private val _state = MutableStateFlow(FavoritesUiState())
    val state: StateFlow<FavoritesUiState> = _state.asStateFlow()

    init {
        refresh()
    }

    fun refresh() {
        viewModelScope.launch {
            _state.update { it.copy(loading = true) }
            runCatching { libraryRepository.favorites() }
                .onSuccess { tracks -> _state.update { it.copy(loading = false, tracks = tracks, error = null) } }
                .onFailure { err -> _state.update { it.copy(loading = false, error = err.message ?: "Error") } }
        }
    }

    fun toggleFavorite(track: TrackDto) {
        viewModelScope.launch {
            val isFav = libraryRepository.toggleFavorite(track.id)
            _state.update { current ->
                current.copy(
                    tracks = if (isFav) {
                        current.tracks.map { if (it.id == track.id) it.copy(is_favorite = isFav) else it }
                    } else {
                        current.tracks.filterNot { it.id == track.id }
                    },
                )
            }
        }
    }

    fun downloadToDevice(track: TrackDto) {
        if (track.file_path.isBlank()) {
            _state.update { it.copy(error = "Este track no tiene archivo descargable") }
            return
        }
        viewModelScope.launch {
            _state.update { it.copy(downloadInProgress = track.id) }
            runCatching {
                fileDownloader.enqueue(track.id, track.file_name.ifBlank { "${track.artist} - ${track.title}.mp3" })
            }
                .onSuccess { _state.update { it.copy(downloadInProgress = null) } }
                .onFailure { err ->
                    _state.update { it.copy(downloadInProgress = null, error = err.message ?: "Error al descargar") }
                }
        }
    }

    fun clearError() {
        _state.update { it.copy(error = null) }
    }
}
