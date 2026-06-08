const board = window.location.pathname.split("/").pop();


// ==========================
// LOAD ITEMS
// ==========================

async function loadItems() {

    let res = await fetch(`/items/${board}`);

    let data = await res.json();

    let container = document.getElementById("items");

    container.innerHTML = "";


    data.forEach(item => {

        container.innerHTML += `

        <div class="card ${item.quantity < item.alert_limit ? 'low-stock' : ''}">

            <div class="card-left">

                <h3>${item.name}</h3>

                <div class="category">
                    ${item.category}
                </div>

                <div class="date-box">

                    <div>
                        Alert Below:
                        ${item.alert_limit}
                    </div>

                    <div>
                        Created:
                        ${item.created_at}
                    </div>

                    <div>
                        Updated:
                        ${item.updated_at}
                    </div>

                </div>

            </div>


            <div class="qty-box">

                <div class="qty-label">
                    Quantity
                </div>

                <div class="qty">
                    ${item.quantity}
                </div>


                ${IS_ADMIN ? `

                <div class="action-buttons">

                    <button
                        class="edit-btn"
                        onclick="updateItem(${item.id})"
                    >
                        Edit
                    </button>

                    <button
                        class="delete-btn"
                        onclick="deleteItem(${item.id})"
                    >
                        Delete
                    </button>

                </div>

                ` : ""}

            </div>

        </div>

        `;
    });

}

///=================

async function importExcel(input) {

    let file = input.files[0];

    if (!file) return;

    let formData = new FormData();

    formData.append("file", file);

    let res = await fetch("/import-excel", {
        method: "POST",
        body: formData
    });

    let result = await res.json();

    alert(result.message);

    loadItems();
}


// ==========================
// ADD ITEM
// ==========================

async function addItem() {

    let name =
        document.getElementById("name").value;

    let category =
        document.getElementById("category").value;

    let quantity = parseInt(

        document.getElementById("quantity").value

    );

    let alertLimit = parseInt(

        document.getElementById("alertLimit").value

    );

    if (!name || !category || !quantity || !alertLimit) {

        Swal.fire({
            icon: "warning",
            title: "Missing Fields",
            text: "Please fill all fields"
        });

        return;
    }

    let res = await fetch(`/items/${board}`, {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            name,
            category,
            quantity,
            alert_limit: alertLimit
        })
    });

    let result = await res.json();

    if (!res.ok) {

        Swal.fire({
            icon: "error",
            title: "Error",
            text: result.message || "Something went wrong"
        });

        return;
    }

    Swal.fire({
        icon: "success",
        title: "Item Added",
        text: "New item added successfully",
        timer: 1500,
        showConfirmButton: false
    });

    closeForm();

    clearForm();

    loadItems();
}


// ==========================
// UPDATE ITEM
// ==========================

async function updateItem(id) {

    const { value: quantity } = await Swal.fire({

        title: "Update Quantity",

        input: "number",

        inputLabel: "Enter new quantity",

        inputPlaceholder: "Quantity",

        confirmButtonText: "Update",

        showCancelButton: true
    });

    if (!quantity) return;

    let res = await fetch(`/items/${id}`, {

        method: "PUT",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            quantity: parseInt(quantity)
        })
    });

    let result = await res.json();

    if (!res.ok) {

        Swal.fire({
            icon: "error",
            title: "Unauthorized",
            text: result.message
        });

        return;
    }

    Swal.fire({
        icon: "success",
        title: "Updated",
        text: "Quantity updated successfully",
        timer: 1500,
        showConfirmButton: false
    });

    loadItems();
}


// ==========================
// DELETE ITEM
// ==========================

async function deleteItem(id) {

    Swal.fire({

        title: "Delete Item?",

        text: "This action cannot be undone",

        icon: "warning",

        showCancelButton: true,

        confirmButtonColor: "#ef4444",

        cancelButtonColor: "#6b7280",

        confirmButtonText: "Yes, Delete"

    }).then(async (result) => {

        if (result.isConfirmed) {

            let res = await fetch(`/items/${id}`, {
                method: "DELETE"
            });

            let data = await res.json();

            if (!res.ok) {

                Swal.fire({
                    icon: "error",
                    title: "Unauthorized",
                    text: data.message
                });

                return;
            }

            Swal.fire({
                icon: "success",
                title: "Deleted",
                text: "Item deleted successfully",
                timer: 1500,
                showConfirmButton: false
            });

            loadItems();
        }
    });
}


// ==========================
// OPEN MODAL
// ==========================

function openForm() {

    document.getElementById(
        "formModal"
    ).style.display = "flex";
}


// ==========================
// CLOSE MODAL
// ==========================

function closeForm() {

    document.getElementById(
        "formModal"
    ).style.display = "none";
}


// ==========================
// CLEAR FORM
// ==========================

function clearForm() {

    document.getElementById("name").value = "";

    document.getElementById("category").value = "";

    document.getElementById("quantity").value = "";

    document.getElementById("alertLimit").value = "";
}


// ==========================
// SEARCH
// ==========================

function searchItems() {

    let input = document

        .getElementById("search")

        .value

        .toLowerCase();

    let cards = document.querySelectorAll(
        ".card"
    );

    cards.forEach(card => {

        let text = card.innerText.toLowerCase();

        if (text.includes(input)) {

            card.style.display = "flex";

        } else {

            card.style.display = "none";
        }
    });
}


// ==========================
// TABLE VIEW
// ==========================

function goToTable() {

    window.location.href =
        `/table/${board}`;
}


// ==========================
// START
// ==========================


function exportExcel() {
    window.location.href = "/export-excel";
}
loadItems();