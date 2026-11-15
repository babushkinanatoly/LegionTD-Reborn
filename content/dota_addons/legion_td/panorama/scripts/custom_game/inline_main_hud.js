// Moved out of layout/custom_game/main_hud.xml: inline <script> tags are no longer supported.

function AddContributor(name, steamId, parent) {
    var newPlayerPanel = $.CreatePanel("Panel", parent, "player_info");
    newPlayerPanel.SetAttributeString("creator_steamid", ""+steamId);
    newPlayerPanel.SetAttributeString("creator_name", name);
    newPlayerPanel.BLoadLayout("file://{resources}/layout/custom_game/legion_creator_panel.xml", false, false);
}

GameUI.CustomUIConfig().Creator.forEach(function(entry){ AddContributor("", entry, $("#Creators"))});
GameUI.CustomUIConfig().ActiveDevelopers.forEach(function(entry){ AddContributor("", entry, $("#ActiveDevs"))});
GameUI.CustomUIConfig().InactiveDevelopers.forEach(function(entry){ AddContributor("", entry, $("#InactiveDevs"))});
