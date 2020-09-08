CREATE SCHEMA stores_target;
go

-- create tables
CREATE TABLE stores_target.categories (
	category_id INT IDENTITY (1, 1) PRIMARY KEY,
	category_name VARCHAR (255) NOT NULL
);

CREATE TABLE stores_target.brands (
	brand_id INT IDENTITY (1, 1) PRIMARY KEY,
	brand_name VARCHAR (255) NOT NULL
);

CREATE TABLE stores_target.products (
	product_id INT IDENTITY (1, 1) PRIMARY KEY,
	product_name VARCHAR (255) NOT NULL,
	brand_id INT NOT NULL,
	category_id INT NOT NULL,
	list_price DECIMAL (10, 2) NOT NULL,
	FOREIGN KEY (category_id) REFERENCES stores_target.categories (category_id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (brand_id) REFERENCES stores_target.brands (brand_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE stores_target.customers (
	customer_id INT IDENTITY (1, 1) PRIMARY KEY,
	last_name VARCHAR (255) NOT NULL,
	first_name VARCHAR (255) NOT NULL,
	phone VARCHAR (25),
	email VARCHAR (255),
	street VARCHAR (255),
	city VARCHAR (50),
	state VARCHAR (25),
	zip_code INT,
	active tinyint NOT NULL,
);


CREATE TABLE stores_target.shops (
	store_id INT IDENTITY (1, 1) PRIMARY KEY,
	store_name VARCHAR (255) NOT NULL,
	phone VARCHAR (25),
	email VARCHAR (255),
	street VARCHAR (255),
	city VARCHAR (255),
	state VARCHAR (10),
	zip_code VARCHAR (5)
);

CREATE TABLE stores_target.employees (
	staff_id INT IDENTITY (1, 1) PRIMARY KEY,
	first_name VARCHAR (50) NOT NULL,
	last_name VARCHAR (255) NOT NULL,
	email VARCHAR (255) NOT NULL,
	phone VARCHAR (25) UNIQUE,
	active tinyint NOT NULL,
	store_id INT NOT NULL,
	manager_id INT,
	FOREIGN KEY (store_id) REFERENCES stores_target.shops (store_id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (manager_id) REFERENCES stores_target.employees (staff_id) ON DELETE NO ACTION ON UPDATE NO ACTION
);

CREATE TABLE stores_target.orders (
	order_id INT IDENTITY (1, 1) PRIMARY KEY,
	customer_id INT,
	order_status tinyint NOT NULL,
	-- Order status: 1 = Pending; 2 = Processing; 3 = Rejected; 4 = Completed
	order_date DATE NOT NULL,
	required_date DATE NOT NULL,
	shipped_date DATE,
	store_id INT NOT NULL,
	staff_id INT NOT NULL,
	FOREIGN KEY (customer_id) REFERENCES stores_target.customers (customer_id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (store_id) REFERENCES stores_target.shops (store_id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (staff_id) REFERENCES stores_target.employees (staff_id) ON DELETE NO ACTION ON UPDATE NO ACTION
);

CREATE TABLE stores_target.order_items (
	order_id INT,
	item_id INT,
	product_id INT NOT NULL,
	quantity INT NOT NULL,
	list_price DECIMAL (10, 2) NOT NULL,
	discount DECIMAL (4, 2) NOT NULL DEFAULT 0,
	PRIMARY KEY (order_id, item_id),
	FOREIGN KEY (order_id) REFERENCES stores_target.orders (order_id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (product_id) REFERENCES stores_target.products (product_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE stores_target.stockdetails (
	store_id INT,
	product_id INT,
	quantity INT,
	PRIMARY KEY (store_id, product_id),
	FOREIGN KEY (store_id) REFERENCES stores_target.shops (store_id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (product_id) REFERENCES stores_target.products (product_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE stores_target.portfolio(
   PortfolioCode            VARCHAR(7) NOT NULL
  ,AccruedInterestLocal     INT  NOT NULL
  ,AccruedInterestBase      INT  NOT NULL
  ,BookCostLocal            INT  NOT NULL
  ,BookCostBase             INT  NOT NULL
  ,ClientSecurityCode       VARCHAR(13) NOT NULL
  ,CollateralUnits          INT  NOT NULL
  ,OriginalCostLocal        INT NOT NULL
  ,OriginalCostBase         INT NOT NULL
  ,LocalCurrencyCode        VARCHAR(3) NOT NULL
  ,PortfolioCurrency        VARCHAR(3) NOT NULL
  ,EffectiveDate            DATE  NOT NULL
  ,ExchangeRateLocaltoBase  INT  NOT NULL
  ,HoldingType              VARCHAR(3) NOT NULL
  ,MarketValueLocal         INT NOT NULL
  ,MarketValueBase          INT NOT NULL
  ,MarketPriceLocalCurrency INT NOT NULL
  ,MarketPriceBase          INT NOT NULL
  ,SecurityNameLong         VARCHAR(31) NOT NULL
  ,NominalQuantity          INT  NOT NULL
  ,CUSIP                    VARCHAR(9) NOT NULL
  ,ISIN                     VARCHAR(12) NOT NULL
  ,PRIMARY KEY(PortfolioCode,ISIN)
);
