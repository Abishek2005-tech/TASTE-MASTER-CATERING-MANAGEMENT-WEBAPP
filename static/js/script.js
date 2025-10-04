document.addEventListener("DOMContentLoaded", function() {
    const scrollElements = document.querySelectorAll(".reveal-on-scroll");

    const elementInView = (el, dividend = 1) => {
        const elementTop = el.getBoundingClientRect().top;
        return (
            elementTop <= (window.innerHeight || document.documentElement.clientHeight) / dividend
        );
    };

    const displayScrollElement = (element) => {
        element.classList.add("is-visible");
    };

    const handleScrollAnimation = () => {
        scrollElements.forEach((el) => {
            if (elementInView(el, 1.25)) {
                displayScrollElement(el);
            }
        });
    };

    window.addEventListener("scroll", () => {
        handleScrollAnimation();
    });

    // Trigger once on load for elements already in view
    handleScrollAnimation();
});
// Add this to your static/js/script.js file

document.addEventListener("DOMContentLoaded", function() {
    // Check if we are on the order summary page
    const quantityInput = document.getElementById('quantity');
    if (quantityInput) {
        const unitPrice = parseFloat(document.querySelector('.item-price').dataset.unitPrice);
        const deliveryFeeElement = document.getElementById('delivery-fee');
        const subtotalElement = document.getElementById('subtotal');
        const totalAmountElement = document.getElementById('total-amount');
        const deliveryOptions = document.querySelectorAll('input[name="delivery_option"]');
        const deliveryFee = 50.00; // Set your delivery fee here

        function updatePrice() {
            const quantity = parseInt(quantityInput.value);
            const subtotal = quantity * unitPrice;
            
            let currentDeliveryFee = 0;
            const selectedDelivery = document.querySelector('input[name="delivery_option"]:checked').value;
            
            if (selectedDelivery === 'delivery') {
                currentDeliveryFee = deliveryFee;
            }
            
            const totalAmount = subtotal + currentDeliveryFee;

            subtotalElement.textContent = `₹${subtotal.toFixed(2)}`;
            deliveryFeeElement.textContent = `₹${currentDeliveryFee.toFixed(2)}`;
            totalAmountElement.textContent = `₹${totalAmount.toFixed(2)}`;
        }

        quantityInput.addEventListener('change', updatePrice);
        deliveryOptions.forEach(option => option.addEventListener('change', updatePrice));

        // Initial price calculation
        updatePrice();
    }
});