package com.mars.auraapp.ui.auth

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.mars.auraapp.data.repo.AuthRepository
import com.mars.auraapp.data.repo.AuthState
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class AuthGateViewModel @Inject constructor(
    private val authRepository: AuthRepository,
) : ViewModel() {

    private val _state = MutableStateFlow<AuthState>(AuthState.Unknown)
    val state: StateFlow<AuthState> = _state.asStateFlow()

    init {
        viewModelScope.launch {
            runCatching { authRepository.refreshAuthStatus() }
                .onFailure { _state.value = AuthState.NeedsLogin(authRequired = true) }
            _state.value = authRepository.authState.value
        }
    }
}

@Composable
fun AuthGate(
    onAuthenticated: @Composable () -> Unit,
    onNeedsLogin: @Composable () -> Unit,
    viewModel: AuthGateViewModel = hiltViewModel(),
) {
    val state by viewModel.state.collectAsState()
    when (state) {
        AuthState.Unknown -> Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator()
        }
        is AuthState.NeedsLogin -> onNeedsLogin()
        AuthState.Authenticated -> onAuthenticated()
    }
}
