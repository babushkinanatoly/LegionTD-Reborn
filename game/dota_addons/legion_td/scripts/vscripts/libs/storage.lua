-- Offline storage stub.
-- The original implementation sent player data, match results, rankings and
-- error logs to external servers (legiontd.n-gao.de / localhost). Those
-- servers are gone, so this stub keeps the same API but never touches the
-- network. Player data lives only in memory for the duration of one match.

Storage = {}
Storage.cachedData = {}
Storage.online = false

local function call(callback, ...)
    if callback ~= nil then
        callback(...)
    end
end

function Storage:GetPlayerData(steam_id, callback)
    call(callback, self.cachedData[steam_id] or {}, true)
end

function Storage:SavePlayerData(steam_id, toStore, callback)
    self.cachedData[steam_id] = toStore
    call(callback, toStore, true)
end

function Storage:SaveMatchData(winner, duration, lastWave, playerData, duelData, callback)
    call(callback, nil, false)
end

function Storage:GetRanking(attribute, from, to, callback)
    call(callback, {}, false)
end

function Storage:GetRankingPosition(attribute, steamId, callback)
    call(callback, {attribute = attribute, steamId = steamId, rank = 0})
end

function Storage:GetMatchHistory(steamId, from, to, callback)
    call(callback, {})
end

function Storage:UpdateUnitData(unitData, callback)
    call(callback)
end

function Storage:UpdateAbilityData(abilityData, callback)
    call(callback)
end

function Storage:UpdateBuilderData(builderData, callback)
    call(callback)
end

function Storage:InvalidateData(steam_id)
    self.cachedData[steam_id] = nil
end

function Storage:InvalidateAll()
    self.cachedData = {}
end

function Storage:LogError(error)
    print("[STORAGE] Error: " .. tostring(error))
end

return Storage
