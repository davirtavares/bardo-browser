var bardoBrowserControllers = angular.module("bardo-browser.controllers", [
    "bardo-browser.services"
]);

bardoBrowserControllers.controller("IndexCtrl", ["$scope",
    function($scope) {
        $scope.test = function() {
            chrome.tabs.getSelected(null, function(tab) {
                chrome.tabs.insertCSS(tab.id, {
                    file: "css/content-style.css"
                });

                chrome.tabs.executeScript(tab.id, {
                    file: "js/prefix.js"
                });

                chrome.tabs.executeScript(tab.id, {
                    file: "js/content-script.js"
                });

              //chrome.pageCapture.saveAsMHTML({ tabId: tab.id }, function (mhtml) {
              //    var mhtmlUrl = window.URL.createObjectURL(mhtml);
              //    chrome.downloads.download({ url: mhtmlUrl, filename: "teste.html" });
              //});
            });
        }
    }
]);
