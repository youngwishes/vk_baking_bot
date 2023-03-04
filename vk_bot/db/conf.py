from sqlalchemy import create_engine, select, Column, ForeignKey, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from contextlib import suppress
from sqlalchemy.exc import NoResultFound

Base = declarative_base()

engine = create_engine(fr"sqlite:///database.db", echo=True, future=True)


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    name = Column(String(40))

    products = relationship(
        "Product", back_populates="category", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"Category(id={self.id}, name={self.name})"


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True)
    name = Column(String(40))
    description = Column(String(512))

    image = Column(String(256))

    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)

    category = relationship("Category", back_populates="products")

    def __repr__(self):
        return f"Product(id={self.id}, name={self.name}, category={self.category})"


Base.metadata.create_all(engine)


class DBManager:
    session = sessionmaker(bind=engine)

    def __init__(self):
        self.delete()
        self.init_data()

    def delete(self):
        with self.session() as sess:
            sess.query(Category).delete(synchronize_session='fetch')
            sess.query(Product).delete(synchronize_session='fetch')
            sess.commit()

    def init_data(self):
        with self.session() as session:
            exclusive_baking = Category(name="Авторская выпечка 🍰")
            croissants = Category(name="Круассаны 🥐")
            donuts = Category(name="Пончики 🍩")
            cakes = Category(name="Торты 🎂")

            chocolate_donut = Product(
                name="Пончик шоколадный",
                description="Наши шоколадные пончики изготовлены из 80% темного шоколада!",
                image=r"media/donuts/chocolate_donut.jpg",
                category=donuts,
            )

            strawberry_donut = Product(
                name="Пончик клубничный",
                description="Наши клубничные пончики изготовлены из настоящей клубники!",
                image=r"media/donuts/strawberry_donut.jpg",
                category=donuts,
            )

            chocolate_croissant = Product(
                name="Круассан шоколадный",
                description="Наши шоколадные круассаны изготовлены из 80% темного шоколада!",
                image=r"media/croissants/chocolate_croissant.jpg",
                category=croissants,
            )

            strawberry_croissant = Product(
                name="Круассан клубничный",
                description="Наши клубничные круассаны изготовлены из настоящей клубники!",
                image=r"media/croissants/strawberry_croissant.jpg",
                category=croissants,
            )

            vanilla_croissant = Product(
                name="Круассан ванильный",
                description="Наши ванильный круассан изготовлен из настоящей ванили!",
                image=r"media/croissants/vanilla_crossant.jpg",
                category=croissants,
            )

            napoleon = Product(
                name="Наполеон",
                description="Наш торт наполеон сделан из самых качественных продуктов.",
                image=r"media/exclusive_baking/наполеон.jpg",
                category=exclusive_baking
            )

            tiramisu = Product(
                name="Тирамису",
                description="Наше тирамиссу просто тает во рту, однозначно рекомендуем!",
                image=r"media/exclusive_baking/тирамису.png",
                category=exclusive_baking
            )

            sharlotka = Product(
                name="Шарлотка",
                description="Наша шарлотка сделана из самых спелых яблок, собранных с любовью.",
                image=r"media/exclusive_baking/sharlotka.jpg",
                category=exclusive_baking
            )

            blue_velvet = Product(
                name="Синий бархат",
                description="Наш синий бархат сделан из самых свежих сливок, собранных с любовью.",
                image=r"media/cakes/синий бархат.jpg",
                category=cakes
            )

            red_velvet = Product(
                name="Красный бархат",
                description="Наш красный бархат сделан из самых свежих сливок, собранных с любовью.",
                image=r"media/cakes/красный бархат.jpg",
                category=cakes
            )

            honey = Product(
                name="Медовик",
                description="Наш медовик сделан из самых свежих сливок,"
                            " собранных с любовью с добавлением настоящего меда.",
                image=r"media/cakes/медовик.jpg",
                category=cakes
            )

            praga = Product(
                name="Прага",
                description="Наша прага сделана из самых свежих сливок,"
                            " собранных с любовью. Приятного аппетита!",
                image=r"media/cakes/прага.jpg",
                category=cakes
            )

            session.add_all(
                [
                    donuts, croissants, exclusive_baking, cakes,
                    vanilla_croissant, chocolate_croissant,
                    strawberry_croissant, chocolate_donut,
                    strawberry_donut, napoleon, sharlotka, tiramisu,
                    blue_velvet, red_velvet, praga, honey
                ]
            )

            session.commit()

    def get_categories(self):
        stmt = select(Category)
        yield from self.session().scalars(stmt).all()

    def get_products(self, category):
        with suppress(NoResultFound):
            stmt = select(Category).where(Category.name == category)
            category = self.session().scalars(stmt).one()

            stmt = select(Product).join(Category.products).where(Product.category_id == category.id)
            yield from self.session().scalars(stmt).all()

    def get_product(self, product_name):
        with suppress(NoResultFound):
            stmt = select(Product).where(Product.name == product_name)
            return self.session().scalars(stmt).one()


def get_db_manager():
    return DBManager()
