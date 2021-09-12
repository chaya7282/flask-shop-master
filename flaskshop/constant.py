import enum

ShipStatusKinds = enum.Enum(value="ShipStatus", names="pending delivered received")
PaymentStatusKinds = enum.Enum(
    value="PaymentStatus", names="waiting preauth confirmed rejected"
)
OrderStatusKinds = enum.Enum(
    value="OrderStatus", names="canceled  unfulfilled fulfilled completed shipped"
)
OrderEvents = enum.Enum(
    value="OrderEvents",
    names="draft_created payment_captured payment_failed order_canceled order_delivered order_completed",
)
DiscountValueTypeKinds = enum.Enum(value="DiscountValueType", names="fixed percent")
VoucherTypeKinds = enum.Enum(
    value="VoucherType", names="product category shipping value"
)

SettingValueType = enum.Enum(
    value="SettingValueType", names="string integer float boolean select selectmultiple"
)
orderProcessing= {
    OrderStatusKinds.canceled.value: {
        "next": OrderStatusKinds.fulfilled.value,
        "prev": None,
    },

     OrderStatusKinds.unfulfilled.value: {
            "next": OrderStatusKinds.fulfilled.value,
            "prev":  OrderStatusKinds.canceled.value,
         },

    OrderStatusKinds.fulfilled.value: {
        "next": OrderStatusKinds.completed.value,
        "prev": None,
    },
    OrderStatusKinds.completed.value: {
        "next": OrderStatusKinds.shipped.value,
        "prev":OrderStatusKinds.fulfilled.value,
    },
    OrderStatusKinds.shipped.value: {
        "next": None,
        "prev": OrderStatusKinds.completed.value,
    },
}




class Permission:
    LOGIN = 0x01
    EDITOR = 0x02
    OPERATOR = 0x04
    ADMINISTER = 0xFF
    PERMISSION_MAP = {
        LOGIN: ("login", "Login user"),
        EDITOR: ("editor", "Editor"),
        OPERATOR: ("op", "Operator"),
        ADMINISTER: ("admin", "Super administrator"),
    }


SiteDefaultSettings = {
    "project_title": {
        "value": "חיה-טק",
        "value_type": SettingValueType.string,
        "name": "Project title",
        "description": "The title of the project.",
    },
    "project_subtitle": {
        "value": "E-commerce Fast and Easy",
        "value_type": SettingValueType.string,
        "name": "Project subtitle",
        "description": "A short description of the project.",
    },
    "project_copyright": {
        "value": "COPYRIGHT © 2021-2022 CHAYA SOFTWARE",
        "value_type": SettingValueType.string,
        "name": "Project Copyright",
        "description": "Copyright notice of the Project like '&copy'. ",
    },
}
