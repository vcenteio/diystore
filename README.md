# DIYStore project

A sample project for an online DIY store using a mix of Domain Driven Design and Clean Architecture.


## Purpose

The main purposes of this project is to learn and show my skills as a programmer.


## Methodology

Before implementation, I like to have a good grasp on requirements and to create user stories. From those, I can dwelve into the problem and derive a model for it. I like to use diagramming, since it helps me to focus on the design part first without having to worry about implementation details, but the diagrams are not "immutable" or constantly being updated: they're just a tool to give a direction to the development of the feature and a basis for its implementation plan.

The implementation part goes from inside out and is driven by testing (TDD). By inside out I mean starting from the core (entities and use cases/services), then building the required infrastructure (database access, caching, external services, etc.) and finally the external interface - which in this case is a REST API - while using mocks and stubs for every dependency and feature not yet developed. When every component of the feature is ready, integration testing comes in.


## Development stage

This is the actual stage the project is in:

Feature #1: Product fetching

- [x] Domain
- [x] Use cases
- [x] Database access with SQLAlchemy
- [ ] REST API with Flask **(under current development)**
- [ ] Server-side caching with Redis

Feature #2: Client authentication
...

Feature #3: Order creation and payment
...

Feature #4: Clients favorite products
...

Feature #5: Sample frontend application (possibly with React and Bootstrap)
...


## Architectural and Design choices

This application is a monolith with its design based on principles of DDD and Clean Architecture.


### <u>Why it's a monolith</u>

The intended scale of the application does require microservices or any other SOA-style architecture, so a monolith is a good choice.


### <u>The layering system</u>

The layering of the application is based on Uncle Bob's Clean Architecture. The entities and use cases form the core of the application and are completely oblivious of whats implemented outside of their boundaries and of whom is using them. They hold the business and application rules and are the reason for the application to exist.


### <u>Communication with the core</u>

The communication to and from the core happens with the usage of DTO's (Data Transfer Objects). They dictate what data has to come in (input DTO) and what data comes out (output DTO). The input DTO also encapsulates the input data validation so that responsibility is taken from the use case/service.

My design diverge in a minor aspect from the Clean Architecure: the use cases return Ouput DTO's instead of data presentations. The reason for that is twofold. First and foremost, I don't think the use case should care that there is a need to present the data to an external interface _in a specific way_ (be it JSON, XML, or any other format). For me, in terms of output, the use case should care only about _what_ information comes out and its up to the adapter or controller to actually create the final presentation. So presenters are called at the infrastructure layer. Secondly, I simply like the symmetry: DTO in, DTO out.


### <u>Use cases as functions, not classes</u>

Since use cases are pure actions that need to be performed by the application, I prefer to use simple functions instead of classes to implement them.


### <u>One repository by domain aggregate</u>

Instead of building one massive respository class, I prefer the DDD way of doing things: one repository by domain aggregate. So if there is a group of classes that are intimatelly connected, are persisted together and share a common root object (like the Product object), then for me it makes sense to build a dedicated repository class specific for that aggregate (for ex: SQLProductRepository).


### <u>Databases and web frameworks do not belong to the core of the application</u>

The usage of an infrastructure layer to encapsulate the communication with databases and web frameworks makes the application highly modular and extensible, which facilitates development and maintenance.


## Tools, libraries and frameworks

The application is built in Python. The following are the main tools that are being used on the project:

**General**:

- Pydantic for data parsing and validation, and for handling configuration
- Pendulum for easier date and time

**Testing**:

- Pytest
- FactoryBoy for simple creation of stubs
- Faker for generating fake data

**Data persistence**:

- SQLAlchemy ORM (with Psycopg2)
- PostgreSQL

**Web**:

- Flask for the REST API
- Postman for API consuming and analysis

**Others**:

- Poetry for managing project dependencies and virtual environments
- Docker for containerization of the application and some external services


## This page will be frequently updated

I'll be updating this page along with the development of the project.
