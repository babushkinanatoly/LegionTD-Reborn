// Moved out of layout/custom_game/my_multiteam_flyout_scoreboard_player.xml: inline <script> tags are no longer supported.

function ToggleMute()
{
    var playerId = $.GetContextPanel().GetAttributeInt( "player_id", -1 );
    if ( playerId !== -1 )
    {
        var newIsMuted = !Game.IsPlayerMuted( playerId );
        Game.SetPlayerMuted( playerId, newIsMuted );
        $.GetContextPanel().SetHasClass( "player_muted", newIsMuted );
    }
}

(function()
{
    var playerId = $.GetContextPanel().GetAttributeInt( "player_id", -1 );
    $.GetContextPanel().SetHasClass( "player_muted", Game.IsPlayerMuted( playerId ) );
})();
