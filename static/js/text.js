//count of the words in the output box
const inputChars = document.querySelector("#input-chars"),
    inputTextElem = document.querySelector(".input-text-area");

inputTextElem.addEventListener("input", (e) => {
  inputChars.innerHTML = inputTextElem.value.length;
});

