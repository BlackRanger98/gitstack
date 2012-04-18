$(document).ready(function(){
	$.ajaxSetup ({     
		// Disable caching of AJAX responses    
		cache: false
	}); 
	
	// hide by default ldap settings
	$('#ldapSettings').hide();

	// retrieve and refresh the settings
	function refreshSettings(){
		$.ajax({
			url: '/rest/settings/authentication/',
			type: "GET",
			dataType: "json",
			success: function(settings){
				if (settings['authMethod'] === 'file'){
					// hide ldap settings
					$('#ldapSettings').hide();

				} else if (settings['authMethod'] === 'ldap'){
					// set ldap radio button
					$("input[name=authMethod]").filter("[value=ldapUsers]").prop("checked",true);

					// show ldap settings
					$('#ldapSettings').show();

					
				}
				
				// fill ldap settings
				$('#ldapUrl').val(settings.ldap.url);
				$('#ldapBindDn').val(settings.ldap.bindDn);
				$('#ldapBindPassword').val(settings.ldap.bindPassword);
			},
			
		});
	}
	
	refreshSettings();
	
	
	
	// click on gitstack users radio button
	$('#gitstackUsers').click(function(){
		// hide ldap settings
		$('#ldapSettings').hide();
	});
	
	// click on ldap users radio button
	$('#ldapUsers').click(function(){
		// show ldap settings
		$('#ldapSettings').show();

	});
	
	// save settings
	$('#saveSettings').click(function(){
		// check which auth method is choosen
		isGitstackUserChecked = $("input[name=authMethod]").filter("[value=gitstackUsers]").prop("checked");
		authMethod = '';
		if(isGitstackUserChecked == true){
			authMethod = 'file';
		} else {
			authMethod = 'ldap';
		}
		
		// construct the json object 
		json_string = '{"authMethod":"' + authMethod + '","ldap":{"url": "' + $('#ldapUrl').val() +'","bindDn": "' + $('#ldapBindDn').val() + '","bindPassword": "' + $('#ldapBindPassword').val() + '"}}';

		// update the settings
		$.ajax({
			url: '/rest/settings/authentication/',
			type: 'PUT',
			contentType: 'application/json',
			data: json_string,
			success: function(data) {
				showMessage("success", data);
			},
			error: function(error) {
				showMessage("error", error.responseText);
			}
		});


	});
	
	/////////////////////////////////
	// Handle notifications 
	///////////////////////////////
	var showMessage = function (messageType, messageText) {
		// Success message
		if(messageType == "success"){
			$('#successMessageBox').show();
			$('#successMessage').html(messageText).show();
			$('#errorMessageBox').hide();
		// error message
		} else if (messageType == "error"){
			$('#successMessageBox').hide();
			$('#errorMessageBox').show();
			$('#errorMessage').html(messageText);
		}
			
	}
	
	
	
	
});