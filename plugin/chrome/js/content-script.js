/**
 * - detectar movimento do mouse e detectar elemento;
 *
 * - ao clicar, injetar DOM;
 *
 * - ao receber mensagem "save" da extensão, coletar todos os elementos
 * selecionados e gerar xpath de todos de volta para a extensão;
 *
 * - a extensão então gera o código da página e junta com os elementos
 * extraídos, e enviar para o webservice persistir;
 */
window.addEventListener("mousemove", function(event) {
    var element = document.elementFromPoint(event.clientX, event.clientY);

    if (element) {
    }
}, true);

window.addEventListener("click", function(event) {
    event.stopPropagation();

    var element = event.target;

    if (element) {
        element.setAttribute(prefix + "-selected", "");
    }
}, true);
