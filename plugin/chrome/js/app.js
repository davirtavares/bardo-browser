var API_ENDPOINT = "http://dev.bardo:8080/api";
//var API_ENDPOINT = "http://localhost:5000";
//var API_ENDPOINT = "http://192.34.56.104:8080/api";

var bardoApp = angular.module("bardo-browser.app", [
    "ngRoute",
    "bardo-browser.services",
    "bardo-browser.controllers",
    "ui.bootstrap"
]);

bardoApp.config(["$routeProvider",
    function($routeProvider) {
        $routeProvider
            .when("/", {
                templateUrl: "partials/main.html",
                controller: "IndexCtrl"
            })

            .otherwise({
                redirectTo: "/"
            });
    }
]);
