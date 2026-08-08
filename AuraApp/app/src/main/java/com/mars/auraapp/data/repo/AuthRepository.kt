package com.mars.auraapp.data.repo

import com.mars.auraapp.data.api.AuthApi
import com.mars.auraapp.data.api.dto.AuthStatusResponse
import com.mars.auraapp.data.api.dto.LoginRequest
import com.mars.auraapp.data.storage.TokenStore
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthRepository @Inject constructor(
    private val authApi: AuthApi,
    private val tokenStore: TokenStore,
) {
    private val _authState = MutableStateFlow<AuthState>(AuthState.Unknown)
    val authState: StateFlow<AuthState> = _authState.asStateFlow()

    suspend fun refreshAuthStatus(): AuthStatusResponse {
        val status = authApi.status()
        val current = _authState.value
        val token = tokenStore.get()
        _authState.value = when {
            !status.auth_required -> AuthState.Authenticated
            !token.isNullOrBlank() -> AuthState.Authenticated
            current is AuthState.Authenticated -> AuthState.Authenticated
            else -> AuthState.NeedsLogin(status.auth_required)
        }
        return status
    }

    suspend fun login(token: String): Boolean {
        val response = authApi.login(LoginRequest(token))
        return if (response.isSuccessful) {
            tokenStore.set(token)
            _authState.value = AuthState.Authenticated
            true
        } else {
            false
        }
    }

    fun logout() {
        tokenStore.clear()
        _authState.value = AuthState.NeedsLogin(authRequired = true)
    }

    fun currentToken(): String? = tokenStore.get()
}

sealed interface AuthState {
    data object Unknown : AuthState
    data class NeedsLogin(val authRequired: Boolean) : AuthState
    data object Authenticated : AuthState
}
