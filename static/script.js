$(document).ready(function () {
    // Booking Page
    var serviceModal = document.getElementById("serviceModal");
    if (serviceModal) {
      serviceModal.addEventListener("show.bs.modal", function (event) {
        // Button that triggered the modal
        var button = event.relatedTarget;

        // Extract info from data-bs-* attributes
        var serviceId = button.getAttribute("data-bs-servId");
        var service = button.getAttribute("data-bs-servName");
        var rate = button.getAttribute("data-bs-servRate");
        var attache = button.getAttribute("data-bs-servAttache");
        var user = button.getAttribute("data-bs-user");
        var client_id = button.getAttribute("data-bs-id");

        // get modal inputs.
        var modalTitle = serviceModal.querySelector(".modal-title");
        var modalClientName = serviceModal.querySelector(
          ".modal-body #clientName"
        );
        var modalAttacheName = serviceModal.querySelector(
          ".modal-body #attacheName"
        );
        var modalClientId = serviceModal.querySelector(".modal-body #client_id");
        var modalServiceRate = serviceModal.querySelector(".modal-body #rate");
        var modalService = serviceModal.querySelector(".modal-body #service");
        var modalServiceId = serviceModal.querySelector(".modal-body #servId");

        // Update the modal's content.
        modalTitle.textContent = service;
        modalClientName.value = user;
        modalAttacheName.value = attache;
        modalClientId.value = client_id;
        modalService.value = service;
        modalServiceRate.value = rate;
        modalServiceId.value = serviceId;
      });
    }

    // Admin Page
    var roleEditModal = document.getElementById("roleEditModal");
    if (roleEditModal) {
      roleEditModal.addEventListener("show.bs.modal", function (event) {
        // trigger button
        let button = event.relatedTarget;

        // extract data-bs attributes
        let staff = button.getAttribute("data-bs-staff");
        let role = button.getAttribute("data-bs-role");

        // get modal inputs
        let modalTitle = roleEditModal.querySelector(".modal-title");
        let modalStaffInput = roleEditModal.querySelector(".modal-body input");

        // update inputs
        modalTitle.textContent = staff;
        modalStaffInput.value = staff;
      });
    }

    // dashboard modal
    let dashboardModal = document.getElementById("dashboardModal");
    if (dashboardModal) {
      dashboardModal.addEventListener("show.bs.modal", function (event) {
        // trigger button
        let button = event.relatedTarget;

        // Extract data-bs attributes
        let clientId = button.getAttribute("data-bs-clientId");
        let serviceId = button.getAttribute("data-bs-serviceId");
        let serviceDate = button.getAttribute("data-bs-serviceDate");
        let serviceRate = button.getAttribute("data-bs-serviceRate");

        // get modal inputs
        let modalClientIdInput = dashboardModal.querySelector(
          ".modal-body #clientId"
        );
        let modalServiceIdInput = dashboardModal.querySelector(
          ".modal-body #serviceId"
        );
        let modalServiceDateInput = dashboardModal.querySelector(
          ".modal-body #serviceDate"
        );
        let modalServiceRateInput = dashboardModal.querySelector(
          ".modal-body #serviceRate"
        );

        // update inputs
        modalClientIdInput.value = clientId;
        modalServiceIdInput.value = serviceId;
        modalServiceDateInput.value = serviceDate;
        modalServiceRateInput.value = serviceRate;
      });
    }

    // filter dashboard tables (to reformat repetetive code!!)
    // table values = 'booked', 'inprogress', 'complete.
    // booked
    let bookedValue = $("#booked").val();
    $("#bookedTableBody tr").filter(function () {
      $(this).toggle($(this).text().toLowerCase().indexOf(bookedValue) > -1);
    });

    // pending
    let inprogressValue = $("#inprogress").val();
    $("#inprogressTableBody tr").filter(function () {
      $(this).toggle($(this).text().toLowerCase().indexOf(inprogressValue) > -1);
    });

    // complete
    let completeValue = $("#complete").val();
    $("#completeTableBody tr").filter(function () {
      $(this).toggle($(this).text().toLowerCase().indexOf(completeValue) > -1);
    });

    // invoice table
    // filter
    $("#inv_select").change(function () {
      var value = $(this).val().toLowerCase();
      $("#inv-body tr").filter(function () {
        $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
      });
      calculate_invoice();
    });

    // invoce total calc
    function calculate_invoice() {
      let invoiceTotal = 0;

      let itemRows = $("#inv-body tr").filter(":visible");

      // loop filtered and update invoiceTotal
      itemRows.each(function () {
        itemTotals = $(this).find("td:nth-child(5)").text();
        console.log("itemTotals scrpt#180", itemTotals);
        invoiceTotal += parseInt(itemTotals);
        $("#invoicedItems tfoot td.total").text(invoiceTotal);
      });
    }
  });
