package com.mars.auraapp

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountBox
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.MusicNote
import androidx.compose.material.icons.filled.QueueMusic
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.adaptive.navigationsuite.NavigationSuiteScaffold
import androidx.compose.material3.adaptive.navigationsuite.NavigationSuiteType
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.mars.auraapp.ui.auth.AuthGate
import com.mars.auraapp.ui.auth.LoginScreen
import com.mars.auraapp.ui.library.FavoritesScreen
import com.mars.auraapp.ui.library.LibraryScreen
import com.mars.auraapp.ui.queue.DownloadQueueScreen
import com.mars.auraapp.ui.search.SearchScreen
import com.mars.auraapp.ui.settings.SettingsScreen
import com.mars.auraapp.ui.theme.AuraAppTheme
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            AuraAppTheme {
                AuthGate(
                    onNeedsLogin = { LoginScreen(onAuthenticated = { /* recompose triggers gate */ }) },
                    onAuthenticated = { AuraAppRoot() },
                )
            }
        }
    }
}

private enum class AuraDestination(
    val route: String,
    val label: String,
    val icon: ImageVector,
) {
    SEARCH("search", "Buscar", Icons.Filled.Home),
    QUEUE("queue", "Cola", Icons.Filled.QueueMusic),
    LIBRARY("library", "Biblioteca", Icons.Filled.AccountBox),
    FAVORITES("favorites", "Favoritos", Icons.Filled.Favorite),
    SETTINGS("settings", "Ajustes", Icons.Filled.MusicNote),
}

@Composable
private fun AuraAppRoot() {
    val navController = rememberNavController()
    var currentDestination by rememberSaveable { mutableStateOf(AuraDestination.SEARCH) }

    NavigationSuiteScaffold(
        layoutType = NavigationSuiteType.NavigationBar,
        navigationSuiteItems = {
            AuraDestination.entries.forEach { dest ->
                item(
                    icon = { Icon(dest.icon, contentDescription = dest.label) },
                    label = { Text(dest.label) },
                    selected = dest == currentDestination,
                    onClick = {
                        if (dest != currentDestination) {
                            currentDestination = dest
                            navController.navigate(dest.route) {
                                popUpTo(navController.graph.startDestinationId) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        }
                    },
                )
            }
        },
    ) {
        Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
            AuraNavHost(
                navController = navController,
                onDestinationChanged = { currentDestination = it },
                modifier = Modifier.padding(innerPadding),
            )
        }
    }
}

@Composable
private fun AuraNavHost(
    navController: NavHostController,
    onDestinationChanged: (AuraDestination) -> Unit,
    modifier: Modifier = Modifier,
) {
    NavHost(
        navController = navController,
        startDestination = AuraDestination.SEARCH.route,
        modifier = modifier,
    ) {
        composable(AuraDestination.SEARCH.route) {
            onDestinationChanged(AuraDestination.SEARCH)
            SearchScreen()
        }
        composable(AuraDestination.QUEUE.route) {
            onDestinationChanged(AuraDestination.QUEUE)
            DownloadQueueScreen()
        }
        composable(AuraDestination.LIBRARY.route) {
            onDestinationChanged(AuraDestination.LIBRARY)
            LibraryScreen()
        }
        composable(AuraDestination.FAVORITES.route) {
            onDestinationChanged(AuraDestination.FAVORITES)
            FavoritesScreen()
        }
        composable(AuraDestination.SETTINGS.route) {
            onDestinationChanged(AuraDestination.SETTINGS)
            SettingsScreen()
        }
    }
}
