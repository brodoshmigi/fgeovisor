import React from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from "yup";
import { Button, BaseButton } from "../styles";

function ResetPasswordPage() {
    const initialValues = {
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
    };

    const validationSchema = Yup.object({
        currentPassword: Yup.string().required("Обязательно"),
        newPassword: Yup.string()
            .min(6, "Минимум 6 символов")
            .required("Обязательно"),
        confirmPassword: Yup.string()
            .oneOf([Yup.ref("newPassword")], "Пароли не совпадают")
            .required("Обязательно"),
    });

    const onSubmit = (values) => {
        console.log("Смена пароля:", values);
        // Запрос на сервер для смены пароля
    };

    return (
        <div>
            <h2>Смена пароля</h2>
            <Formik
                initialValues={initialValues}
                validationSchema={validationSchema}
                onSubmit={onSubmit}
            >
                <Form>
                    <div>
                        <label htmlFor="currentPassword">Текущий пароль:</label>
                        <Field type="password" name="currentPassword" />
                        <ErrorMessage
                            name="currentPassword"
                            component="div"
                            style={{ color: "red" }}
                        />
                    </div>
                    <div>
                        <label htmlFor="newPassword">Новый пароль:</label>
                        <Field type="password" name="newPassword" />
                        <ErrorMessage
                            name="newPassword"
                            component="div"
                            style={{ color: "red" }}
                        />
                    </div>
                    <div>
                        <label htmlFor="confirmPassword">
                            Подтвердите новый пароль:
                        </label>
                        <Field type="password" name="confirmPassword" />
                        <ErrorMessage
                            name="confirmPassword"
                            component="div"
                            style={{ color: "red" }}
                        />
                    </div>
                    <Button type="submit">Сменить пароль</Button>
                </Form>
            </Formik>
        </div>
    );
}

export default ResetPasswordPage;
