
# The Little Lemon Menu & Booking API

![Little Lemon Logo](https://cdn.jsdelivr.net/gh/Terry-BrooksJr/be_capstone@4a8b3aefa77fcee2b21704b10f8b5facb865ea2e/applications/resturant/static/restaurant/img/logo.png)

Welcome to the Little Lemon  Menu & Booking API, a RESTful API designed for inventory and reservation management.

This project is developed as a final assignment for Meta's Backend Engineering Capstone Course on Coursera by Terry Brooks. You can find the [course on Coursera](https://www.coursera.org/learn/back-end-developer-capstone/home/info) and the project source code on GitHub.

> [!WARNING]
> This project is open-source for learning purposes, but please respect Coursera’s academic honesty policy. Refer to the Coursera Honor Code for guidance.

## Table of Contents

- [The Little Lemon Menu \& Booking API](#the-little-lemon-menu--booking-api)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
    - [Features](#features)
  - [Getting Started](#getting-started)
    - [Testing/Touring the Mock API](#testingtouring-the-mock-api)
      - [_Which ever Method Selected, The Getting Started Steps are the Same_!](#which-ever-method-selected-the-getting-started-steps-are-the-same)
      - [Routes To Test:](#routes-to-test)
  - [API Documentation](#api-documentation)


## Overview

The Little Lemon   Menu & Booking APII offers a collection of endpoints to manage user accounts, menu items, and reservations supports user registration, token-based authentication, and various managerial functions.

### Features

- **User Management:** Registatation,authentication of consumers 
- **Inventory Management:** CRUD operations on menu items.
- **Reservation Management:** CRUD Operations on reservations 

## Getting Started

### Testing/Touring the Mock API

To explore the API without setting up a local environment, you can use the tour the API via:

- #### [Postman](https://www.postman.com/blackberry-py-dev/workspace/little-lemon-meta-apis-final-terry-brooks-jr)
- Fully documented [Postman](https://www.postman.com/) Workspace, that has helpful request automnation scripting.
- #### [DRF Browseable API UI](https://api.little-lemon.xyz)
- The native browser based API interface provided by [Django Rest Framework](https://www.django-rest-framework.org/).
- #### [Swagger UI](https://api.little-lemon.xyz/api/swagger)
- Browser Based API interface using the [Swagger UI](https://swagger.io/)
- #### BYOC Bring Your Own Client
- Any HTTP Client your heart desires using the `https://api.little-lemon.xyz` and the documentation found via [Postman](https://www.postman.com/blackberry-py-dev/workspace/little-lemon-meta-apis-final-terry-brooks-jr) or e[ReDoc](https://api.little-lemon.xyz/api/docs)

#### _Which ever Method Selected, The Getting Started Steps are the Same_!

#### Routes To Test: 
- `/auth/users` - Register an accounts
- `/auth/`
- `/restaurant/bookings/`
- `/restaurant/bookings/<random_interger>` _(Reservations IDs 1-62 Available)_
- `/restaurant/menu/`
- `/restaurant/menu/<random_interger>` _(Menu IDs 1 -145 Available)
  
## API Documentation

The API follows the OpenAPI 3.0 standard. Here are the main route categories:
