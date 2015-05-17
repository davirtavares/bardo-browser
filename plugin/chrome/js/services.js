var bardoBrowserServices = angular.module("bardo-browser.services", [
]);

bardoBrowserServices.factory("Dialogs", ["$modal",
    function($modal) {
        return {
            errorDialog: function(message, title) {
                return $modal.open({
                    templateUrl: "dialogs/error.html",

                    controller: "ErrorDialogCtrl",

                    resolve: {
                        data: function() {
                            return {
                                message: message,
                                title: title
                            }
                        }
                    }
                }).result;
            },

            confirmDialog: function(message, title) {
                return $modal.open({
                    templateUrl: "dialogs/confirm.html",

                    controller: "ConfirmDialogCtrl",

                    resolve: {
                        data: function() {
                            return {
                                message: message,
                                title: title
                            }
                        }
                    }
                }).result;
            }
        }
    }
]);

bardoBrowserServices.controller("ErrorDialogCtrl", ["$scope", "data",
    function($scope, data) {
        $scope.message = data.message;
        $scope.title = data.title || "Error";
    }
]);

bardoBrowserServices.controller("ConfirmDialogCtrl", ["$scope", "data",
    function($scope, data) {
        $scope.message = data.message;
        $scope.title = data.title || "Confirm action";
    }
]);
