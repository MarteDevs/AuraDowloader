package com.mars.auraapp.data.storage

interface TokenStore {
    fun get(): String?
    fun set(token: String)
    fun clear()
}
