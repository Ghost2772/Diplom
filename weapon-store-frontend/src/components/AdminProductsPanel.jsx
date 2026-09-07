import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { createAdminProduct, updateAdminProduct, uploadProductImage } from "../api/adminApi";
import { getApiErrorMessage } from "../utils/apiErrors";
import ConfirmDialog from "./ConfirmDialog";
import ProductImage from "./ProductImage";

const money = new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB" });
const MAX_IMAGE_BYTES = 8 * 1024 * 1024;

function initialForm(product, categories) {
  return {
    name: product?.name || "",
    sku: product?.sku || "",
    brand: product?.brand || "",
    category_id: String(product?.category_id || categories[0]?.id || ""),
    price: product?.price == null ? "" : String(product.price),
    old_price: product?.old_price == null ? "" : String(product.old_price),
    stock: String(product?.stock ?? 0),
    short_description: product?.short_description || "",
    description: product?.description || "",
    image_url: product?.image_url || "",
    is_active: product?.is_active ?? true,
    is_featured: product?.is_featured ?? false,
    is_regulated: product?.is_regulated ?? false,
    specs: Object.entries(product?.attributes || {}).map(([name, value], index) => ({
      id: `saved-${index}`, name, value,
    })),
  };
}

function ProductEditor({ product, categories, onSave, onCancel }) {
  const [initial] = useState(() => initialForm(product, categories));
  const [form, setForm] = useState(initial);
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [busy, setBusy] = useState(false);
  const [progress, setProgress] = useState("");
  const [error, setError] = useState("");
  const [confirmDiscard, setConfirmDiscard] = useState(false);
  const previewRef = useRef("");
  const busyRef = useRef(false);
  const errorRef = useRef(null);
  const headingRef = useRef(null);
  const dirty = JSON.stringify(form) !== JSON.stringify(initial) || Boolean(selectedFile);

  useEffect(() => {
    headingRef.current?.focus();
    return () => { if (previewRef.current) URL.revokeObjectURL(previewRef.current); };
  }, []);

  useEffect(() => {
    if (!dirty) return;
    const preventClose = (event) => { event.preventDefault(); event.returnValue = ""; };
    window.addEventListener("beforeunload", preventClose);
    return () => window.removeEventListener("beforeunload", preventClose);
  }, [dirty]);

  useEffect(() => { if (error) errorRef.current?.focus(); }, [error]);

  const change = (name, value) => setForm((current) => ({ ...current, [name]: value }));
  const replaceFile = (file) => {
    if (previewRef.current) URL.revokeObjectURL(previewRef.current);
    previewRef.current = file ? URL.createObjectURL(file) : "";
    setPreview(previewRef.current);
    setSelectedFile(file);
  };

  const handleFile = (event) => {
    const file = event.target.files[0];
    event.target.value = "";
    if (!file) return;
    if (!["image/png", "image/jpeg", "image/webp"].includes(file.type)) {
      setError("Выберите изображение PNG, JPEG или WebP");
      return;
    }
    if (file.size > MAX_IMAGE_BYTES) {
      setError("Размер изображения не должен превышать 8 МБ");
      return;
    }
    setError("");
    replaceFile(file);
  };

  const changeSpec = (id, name, value) => setForm((current) => ({
    ...current,
    specs: current.specs.map((spec) => spec.id === id ? { ...spec, [name]: value } : spec),
  }));

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (busyRef.current) return;
    const attributes = Object.create(null);
    const names = new Set();
    for (const spec of form.specs) {
      const name = spec.name.trim();
      const value = spec.value.trim();
      if (!name && !value) continue;
      if (!name || !value) {
        setError("Заполните название и значение каждой характеристики или удалите пустую строку");
        return;
      }
      if (names.has(name.toLocaleLowerCase("ru-RU"))) {
        setError(`Характеристика «${name}» указана дважды`);
        return;
      }
      names.add(name.toLocaleLowerCase("ru-RU"));
      attributes[name] = value;
    }
    if (form.old_price && Number(form.old_price) <= Number(form.price)) {
      setError("Старая цена должна быть больше текущей");
      return;
    }
    busyRef.current = true;
    setBusy(true);
    setError("");
    try {
      let imageUrl = form.image_url.trim() || null;
      if (selectedFile) {
        setProgress("Загружаем изображение…");
        imageUrl = await uploadProductImage(selectedFile);
        change("image_url", imageUrl);
        replaceFile(null);
      }
      setProgress("Сохраняем товар…");
      const payload = {
        name: form.name.trim(), sku: form.sku.trim(), brand: form.brand.trim() || null,
        category_id: Number(form.category_id), price: form.price,
        old_price: form.old_price || null, stock: Number(form.stock),
        short_description: form.short_description.trim() || null,
        description: form.description.trim() || null, image_url: imageUrl, attributes,
        is_active: form.is_active, is_featured: form.is_featured, is_regulated: form.is_regulated,
        slug: product?.slug || null,
      };
      const saved = product
        ? await updateAdminProduct(product.id, payload)
        : await createAdminProduct(payload);
      onSave(saved);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "Не удалось сохранить товар. Попробуйте ещё раз"));
    } finally {
      busyRef.current = false;
      setBusy(false);
      setProgress("");
    }
  };

  return (
    <>
      <div className="admin-section__heading">
        <div>
          <p>{product ? "Редактирование каталога" : "Конструктор товара"}</p>
          <h2 ref={headingRef} tabIndex={-1}>{product ? product.name : "Новый товар"}</h2>
        </div>
        <button type="button" className="admin-refresh" disabled={busy}
          onClick={() => dirty ? setConfirmDiscard(true) : onCancel()}>К списку товаров</button>
      </div>
      <form className="admin-product-editor" onSubmit={handleSubmit} aria-busy={busy}>
        <div className="admin-product-editor__fields">
          {error && <div ref={errorRef} tabIndex={-1} className="workspace-notice workspace-notice--error" role="alert">{error}</div>}
          <fieldset className="glass-panel product-form-section" disabled={busy}>
            <legend>Основная информация</legend>
            <div className="product-form-grid">
              <label className="product-form-field product-form-field--wide">
                <span>Название товара</span>
                <input required minLength={2} maxLength={150} value={form.name}
                  onChange={(event) => change("name", event.target.value)} placeholder="Название модели или товара" />
              </label>
              <label className="product-form-field"><span>Артикул</span>
                <input required minLength={2} maxLength={64} value={form.sku}
                  onChange={(event) => change("sku", event.target.value)} placeholder="Например, MF-OPT-0002" />
              </label>
              <label className="product-form-field"><span>Бренд</span>
                <input maxLength={100} value={form.brand} onChange={(event) => change("brand", event.target.value)} placeholder="Производитель" />
              </label>
              <label className="product-form-field product-form-field--wide"><span>Категория</span>
                <select required value={form.category_id} onChange={(event) => change("category_id", event.target.value)}>
                  <option value="" disabled>Выберите категорию</option>
                  {categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
                </select>
              </label>
              <label className="product-form-field"><span>Цена, ₽</span>
                <input type="number" required min="0.01" max="99999999.99" step="0.01" value={form.price}
                  onChange={(event) => change("price", event.target.value)} placeholder="0,00" />
              </label>
              <label className="product-form-field"><span>Старая цена, ₽</span>
                <input type="number" min="0.01" max="99999999.99" step="0.01" value={form.old_price}
                  onChange={(event) => change("old_price", event.target.value)} placeholder="Необязательно" />
              </label>
              <label className="product-form-field"><span>Остаток</span>
                <input type="number" required min="0" max="2147483647" step="1" value={form.stock}
                  onChange={(event) => change("stock", event.target.value)} />
                <small>Для упакованных товаров — число упаковок</small>
              </label>
            </div>
          </fieldset>

          <fieldset className="glass-panel product-form-section" disabled={busy}>
            <legend>Описание</legend>
            <label className="product-form-field"><span>Краткое описание</span>
              <textarea rows={2} maxLength={300} value={form.short_description}
                onChange={(event) => change("short_description", event.target.value)} placeholder="Главное о товаре для карточки каталога" />
              <small>{form.short_description.length}/300</small>
            </label>
            <label className="product-form-field"><span>Полное описание</span>
              <textarea rows={6} maxLength={5000} value={form.description}
                onChange={(event) => change("description", event.target.value)} placeholder="Описание для страницы товара" />
            </label>
          </fieldset>

          <fieldset className="glass-panel product-form-section" disabled={busy}>
            <legend>Характеристики</legend>
            <p className="product-form-hint">Добавьте параметры товара — они появятся на его странице</p>
            <div className="product-spec-rows">
              {form.specs.map((spec, index) => (
                <div className="product-spec-row" key={spec.id}>
                  <input aria-label={`Название характеристики ${index + 1}`} maxLength={80} value={spec.name}
                    onChange={(event) => changeSpec(spec.id, "name", event.target.value)} placeholder="Например, Калибр" />
                  <input aria-label={`Значение характеристики ${index + 1}`} maxLength={240} value={spec.value}
                    onChange={(event) => changeSpec(spec.id, "value", event.target.value)} placeholder="Значение" />
                  <button type="button" className="product-spec-remove" aria-label={`Удалить характеристику ${index + 1}`}
                    onClick={() => change("specs", form.specs.filter((item) => item.id !== spec.id))}>×</button>
                </div>
              ))}
            </div>
            <button type="button" className="admin-refresh" disabled={form.specs.length >= 40}
              onClick={() => change("specs", [...form.specs, { id: crypto.randomUUID(), name: "", value: "" }])}>
              + Добавить характеристику
            </button>
            <p className="product-form-hint">Для упаковок добавьте «Количество в упаковке», например «10 шт»</p>
          </fieldset>

          <fieldset className="glass-panel product-form-section" disabled={busy}>
            <legend>Отображение</legend>
            {[["is_active", "Показывать в каталоге"], ["is_featured", "Рекомендуемый товар"],
              ["is_regulated", "Требуется проверка документов"]].map(([key, label]) => (
              <label className="product-form-check" key={key}>
                <input type="checkbox" checked={form[key]} onChange={(event) => change(key, event.target.checked)} />
                <span>{label}</span>
              </label>
            ))}
          </fieldset>
        </div>

        <aside className="admin-product-editor__preview">
          <fieldset className="glass-panel product-form-section" disabled={busy}>
            <legend>Изображение и предпросмотр</legend>
            <div className="product-editor-preview">
              <ProductImage src={preview || form.image_url} name={form.name || "Новый товар"} />
              <p>{categories.find((category) => String(category.id) === form.category_id)?.name}</p>
              <h3>{form.name || "Название товара"}</h3>
              <span>{form.short_description || "Краткое описание появится здесь"}</span>
              <strong>{Number(form.price) > 0 ? money.format(Number(form.price)) : "Укажите цену"}</strong>
              {!form.is_active && <small>Скрыт из каталога</small>}
            </div>
            <label className="product-image-upload">
              <span>{selectedFile ? "Заменить фотографию" : "Загрузить фотографию"}</span>
              <input type="file" accept="image/png,image/jpeg,image/webp" onChange={handleFile} aria-label="Загрузить фотографию товара" />
            </label>
            <p className="product-form-hint">PNG, JPEG или WebP · до 8 МБ · до 20 Мп</p>
            {selectedFile && <p className="product-form-hint">Выбрано: {selectedFile.name}</p>}
            <label className="product-form-field"><span>Или ссылка на изображение</span>
              <input type="text" maxLength={500} value={form.image_url} disabled={busy || Boolean(selectedFile)}
                onChange={(event) => change("image_url", event.target.value)} placeholder="https://… или /images/…" />
            </label>
            {(selectedFile || form.image_url) && <button type="button" className="admin-refresh"
              onClick={() => { replaceFile(null); change("image_url", ""); }}>Убрать изображение</button>}
          </fieldset>
          <div className="glass-panel product-editor-actions">
            <p role="status">{progress || "Изменения появятся в каталоге после сохранения"}</p>
            <button className="product-save-button" type="submit" disabled={busy || !categories.length}>
              {busy ? "Сохраняем…" : product ? "Сохранить изменения" : "Создать товар"}
            </button>
          </div>
        </aside>
      </form>
      {confirmDiscard && <ConfirmDialog title="Отменить изменения?" confirmLabel="Отменить изменения"
        onCancel={() => setConfirmDiscard(false)} onConfirm={onCancel}>
        Несохранённые изменения в форме будут потеряны
      </ConfirmDialog>}
    </>
  );
}

export default function AdminProductsPanel({ products, categories, onProductsChange, onEditorChange }) {
  const [editor, setEditor] = useState(null);
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [notice, setNotice] = useState("");
  const openEditor = (product) => { setEditor({ product }); onEditorChange(true); setNotice(""); };
  const closeEditor = () => { setEditor(null); onEditorChange(false); };
  const handleSave = (saved) => {
    onProductsChange((current) => current.some((item) => item.id === saved.id)
      ? current.map((item) => item.id === saved.id ? saved : item)
      : [...current, saved]);
    setSearch("");
    setCategoryFilter("");
    setNotice(`Товар «${saved.name}» ${editor.product ? "обновлён" : "создан"}`);
    closeEditor();
  };
  const visible = products.filter((product) =>
    `${product.name} ${product.sku} ${product.brand || ""}`.toLocaleLowerCase("ru-RU")
      .includes(search.trim().toLocaleLowerCase("ru-RU")) &&
    (!categoryFilter || String(product.category_id) === categoryFilter));

  return (
    <section className="admin-section" role="tabpanel" aria-label="Товары">
      {editor ? <ProductEditor key={editor.product?.id || "new"} product={editor.product}
        categories={categories} onSave={handleSave} onCancel={closeEditor} /> : <>
        <div className="admin-section__heading">
          <div><p>Управление ассортиментом</p><h2>Товары каталога</h2></div>
          <button type="button" className="product-save-button" disabled={!categories.length}
            onClick={() => openEditor(null)}>+ Новый товар</button>
        </div>
        {notice && <div className="workspace-notice workspace-notice--success" role="status">{notice}</div>}
        <div className="admin-product-filters">
          <input type="search" value={search} onChange={(event) => setSearch(event.target.value)}
            placeholder="Название, артикул или бренд" aria-label="Поиск товаров" />
          <select value={categoryFilter} onChange={(event) => setCategoryFilter(event.target.value)} aria-label="Фильтр по категории">
            <option value="">Все категории</option>
            {categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
          </select>
        </div>
        {visible.length === 0 ? <div className="glass-panel admin-empty">Товары не найдены</div> : (
          <div className="admin-products-list">
            {visible.map((product) => (
              <article className="glass-panel admin-product-row" key={product.id}>
                <ProductImage src={product.image_url} name={product.name} />
                <div className="admin-product-row__name">
                  <span>{product.sku} · {categories.find((category) => category.id === product.category_id)?.name}</span>
                  <Link to={`/products/${product.id}`}>{product.name} ↗</Link>
                  <small className={product.is_active ? "is-active" : ""}>
                    {product.is_active ? "В каталоге" : "Скрыт из каталога"}
                  </small>
                </div>
                <div className="admin-product-row__price"><strong>{money.format(Number(product.price))}</strong>
                  <span>Остаток: {product.stock} {product.attributes?.["Количество в упаковке"] ? "уп" : "шт"}</span>
                </div>
                <button type="button" className="admin-refresh" onClick={() => openEditor(product)}
                  aria-label={`Редактировать ${product.name}`}>Редактировать</button>
              </article>
            ))}
          </div>
        )}
      </>}
    </section>
  );
}
