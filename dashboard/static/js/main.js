"use strict";


document.addEventListener("DOMContentLoaded", () => {

    initializeLoader();

    initializeSidebar();

    initializeFlashMessages();

    initializeRefreshButton();

    initializeClock();

    initializeSectionNav();

});


/* =============================================================
   LOADING SCREEN
============================================================= */

function initializeLoader() {

    const loader =
        document.getElementById("loader");

    if (!loader) {
        return;
    }


    const born = performance.now();

    let hidden = false;


    function ready(action) {

        const elapsed = performance.now() - born;

        const wait = Math.max(0, 3000 - elapsed);

        setTimeout(action, wait);
    }


    function hide() {

        if (hidden || !document.body.contains(loader)) {
            return;
        }

        hidden = true;

        loader.classList.add("is-hidden");

        loader.addEventListener(
            "transitionend",
            () => loader.remove(),
            { once: true }
        );
    }


    const finish = () => ready(hide);


    if (document.readyState === "complete") {

        finish();

    } else {

        window.addEventListener("load", finish);

    }


    setTimeout(hide, 9000);

}


/* =============================================================
   SIDEBAR
============================================================= */

function initializeSidebar() {

    const sidebar =
        document.getElementById("sidebar");

    const menuToggle =
        document.getElementById("menuToggle");

    const overlay =
        document.getElementById("sidebarOverlay");


    if (!sidebar) {
        return;
    }


    function openSidebar() {

        sidebar.classList.add("open");

        if (overlay) {
            overlay.classList.add("active");
        }

        document.body.style.overflow = "hidden";
    }


    function closeSidebar() {

        sidebar.classList.remove("open");

        if (overlay) {
            overlay.classList.remove("active");
        }

        document.body.style.overflow = "";
    }


    if (menuToggle) {

        menuToggle.addEventListener(
            "click",
            openSidebar
        );

    }


    if (overlay) {

        overlay.addEventListener(
            "click",
            closeSidebar
        );

    }


    document.addEventListener(
        "keydown",
        (event) => {

            if (event.key === "Escape") {
                closeSidebar();
            }

        }
    );

}


/* =============================================================
   FLASH MESSAGES
============================================================= */

function initializeFlashMessages() {

    const messages =
        document.querySelectorAll(
            ".flash-message"
        );


    messages.forEach((message) => {

        const closeButton =
            message.querySelector(
                ".flash-close"
            );


        if (closeButton) {

            closeButton.addEventListener(
                "click",
                () => {

                    message.remove();

                }
            );

        }


        setTimeout(() => {

            if (message.parentNode) {
                message.remove();
            }

        }, 5000);

    });

}


/* =============================================================
   REFRESH
============================================================= */

function initializeRefreshButton() {

    const button =
        document.getElementById(
            "refreshButton"
        );


    if (!button) {
        return;
    }


    button.addEventListener(
        "click",
        () => {

            button.disabled = true;

            window.location.reload();

        }
    );

}


/* =============================================================
   SECTION NAVIGATION (zoom to dashboard part)
============================================================= */

function initializeSectionNav() {

    const navItems = Array.from(
        document.querySelectorAll(
            ".sidebar-nav .nav-item[href^='#']"
        )
    );

    if (!navItems.length) {
        return;
    }

    const sections = navItems
        .map((item) => document.querySelector(item.getAttribute("href")))
        .filter((section) => section !== null);


    navItems.forEach((item) => {

        item.addEventListener("click", () => {

            navItems.forEach((n) => n.classList.remove("active"));

            item.classList.add("active");

        });

    });


    if (!("IntersectionObserver" in window) || !sections.length) {
        return;
    }

    const spy = new IntersectionObserver(
        (entries) => {

            entries.forEach((entry) => {

                if (!entry.isIntersecting) {
                    return;
                }

                const id = `#${entry.target.id}`;

                navItems.forEach((n) => {
                    n.classList.toggle(
                        "active",
                        n.getAttribute("href") === id
                    );
                });

            });

        },
        { rootMargin: "-35% 0px -60% 0px" }
    );

    sections.forEach((section) => spy.observe(section));

}


/* =============================================================
   LIVE CLOCK + FRESHNESS
============================================================= */

function initializeClock() {

    const clock =
        document.getElementById("clock");

    const statusClock =
        document.getElementById("statusClock");


    function pad(n) {
        return String(n).padStart(2, "0");
    }


    function update() {

        const now = new Date();
        const time = `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;

        if (clock) {
            clock.textContent = time;
        }

        if (statusClock) {
            statusClock.textContent = `${time} LOCAL`;
        }

    }

    update();

    setInterval(update, 1000);

}