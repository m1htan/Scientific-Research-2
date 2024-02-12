function increaseQuantity(quantityId) {
  var input = document.getElementById(quantityId);
  var currentValue = parseInt(input.value);
  input.value = currentValue + 1;
}

function decreaseQuantity(quantityId) {
  var input = document.getElementById(quantityId);
  var currentValue = parseInt(input.value);
  if (currentValue > 1) {
    input.value = currentValue - 1;
  }
}

function addToCart(id) {
  var quantity = document.getElementById("quantity").value;
  // Gửi yêu cầu AJAX đến Flask
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/add_to_cart/" + id + "?quantity=" + quantity, true);
  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4 && xhr.status == 200) {
      alert("The product has been added to cart.");
    }
  };
  xhr.send();
}

document.addEventListener("DOMContentLoaded", function () {
  var cart = JSON.parse(localStorage.getItem("cart")) || [];
  cart.forEach(function (item) {
    var productElement = document.getElementById("quantity-" + item.id);
    if (productElement) {
      productElement.value = item.quantity;
    }
  });
});
