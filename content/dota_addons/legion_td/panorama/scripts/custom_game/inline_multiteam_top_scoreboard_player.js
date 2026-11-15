// Moved out of layout/custom_game/multiteam_top_scoreboard_player.xml: inline <script> tags are no longer supported.

function PortraitClicked()
{
    // TODO: ctrl and alt click support
    Players.PlayerPortraitClicked( $.GetContextPanel().GetAttributeInt( "player_id", -1 ), false, false );
}
