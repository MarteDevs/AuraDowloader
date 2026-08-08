package com.mars.auraapp.ui.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.mars.auraapp.data.api.dto.PublicSettings
import com.mars.auraapp.data.repo.AuthRepository
import com.mars.auraapp.data.repo.SettingsRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class SettingsUiState(
    val settings: PublicSettings? = null,
    val loading: Boolean = false,
    val error: String? = null,
    val loggedOut: Boolean = false,
)

@HiltViewModel
class SettingsViewModel @Inject constructor(
    private val settingsRepository: SettingsRepository,
    private val authRepository: AuthRepository,
) : ViewModel() {

    private val _state = MutableStateFlow(SettingsUiState())
    val state: StateFlow<SettingsUiState> = _state.asStateFlow()

    init {
        refresh()
    }

    fun refresh() {
        viewModelScope.launch {
            _state.update { it.copy(loading = true) }
            runCatching { settingsRepository.get() }
                .onSuccess { s -> _state.update { it.copy(loading = false, settings = s, error = null) } }
                .onFailure { err -> _state.update { it.copy(loading = false, error = err.message ?: "Error") } }
        }
    }

    fun logout() {
        authRepository.logout()
        _state.update { it.copy(loggedOut = true) }
    }

    fun clearError() {
        _state.update { it.copy(error = null) }
    }
}
