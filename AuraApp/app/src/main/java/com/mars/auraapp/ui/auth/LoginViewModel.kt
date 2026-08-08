package com.mars.auraapp.ui.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.mars.auraapp.data.repo.AuthRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class LoginUiState(
    val token: String = "",
    val loading: Boolean = false,
    val error: String? = null,
    val success: Boolean = false,
)

@HiltViewModel
class LoginViewModel @Inject constructor(
    private val authRepository: AuthRepository,
) : ViewModel() {

    private val _state = MutableStateFlow(LoginUiState())
    val state: StateFlow<LoginUiState> = _state.asStateFlow()

    fun onTokenChange(value: String) {
        _state.update { it.copy(token = value, error = null) }
    }

    fun submit() {
        val current = _state.value
        if (current.token.isBlank() || current.loading) return
        _state.update { it.copy(loading = true, error = null) }
        viewModelScope.launch {
            val ok = runCatching { authRepository.login(current.token.trim()) }
                .getOrElse { e ->
                    _state.update { it.copy(loading = false, error = e.message ?: "Error de red") }
                    return@launch
                }
            if (ok) {
                _state.update { it.copy(loading = false, success = true) }
            } else {
                _state.update { it.copy(loading = false, error = "Token inválido") }
            }
        }
    }
}
