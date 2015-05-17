var bardoBrowserControllers = angular.module("bardo-browser.controllers", [
    "bardo-browser.services"
]);

bardoBrowserControllers.controller("IndexCtrl", ["$scope",
    function($scope) {
        $scope.test = function() {
            chrome.tabs.getSelected(null, function(tab) {
                chrome.pageCapture.saveAsMHTML({ tabId: tab.id }, function (mhtml) {
                    var mhtmlUrl = window.URL.createObjectURL(mhtml);

                    chrome.downloads.download({ url: mhtmlUrl, filename: "teste.html" });
                });
            });
        }
    }
]);
