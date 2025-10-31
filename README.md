# McDonald's receipt code analysis (unofficial)

An attempt to reverse engineer the 12 digit codes found on McDonald's receipts used for the [Food for Thoughts](https://www.mcdfoodforthoughts.com/) survey.

> [!IMPORTANT]
> **Disclaimer**

This project is an independent, educational analysis of McDonald's UK receipts.

It is **not** affiliated with, endorsed by, or connected to McDonald's International Property Company, Ltd.

The contents of this repository represent speculative research based on publicly available information, and are provided here for research and educational purposes only.

No part of this project is intended to enable or encourage misuse, fraud, or unauthorised access to McDonald's systems.

_Polite notice to McLawyers:_ the french fries emoji, 🍟, is not McDonald's intellectual property; it's a Unicode character.

## How to use

Call the script with the following arguments:

```shell
python get_code.py --store-id 1553 --order-id 1743 --purchased "2023-03-14 16:48"
```

The above will reproduce a known historical code, `7ZWW-NGH3-ZFWJ`, as shown in the following receipt:

![Receipt showing code 7ZWW-NGH3-ZFWJ](./assets/7ZWW-NGH3-ZFWJ.jpg)

Note the receipt contains `REG 20` - this is the default value used in the script, but not all receipts have the same value.

## Algorithm speculation

The survey code above appears to be broken down as follows:

| Code    | Decimal   | Meaning                                                                                                                                  |
| -       | -         | -                                                                                                                                        |
| `7ZW`   | 1553      | Store ID.                                                                                                                                |
| `WNG`   | 2043      | Usually seems to be a combination of the "reg" number multiplied by 100 + the order ID's last two digits. In this case: (20 * 100) + 43. |
| `H3ZFW` | 3,742,128 | Date/time of purchase (represented as number of minutes since `2016-02-01 00:00`).                                                       |
| `J`     | 23        | Check digit (Luhn mod _N_ algorithm; uses 25 as a base).                                                                                 |

Values are encoded using the following base 25 system:

<table>
    <tbody>
        <tr>
            <th>Decimal</th>
            <td>0</td>
            <td>1</td>
            <td>2</td>
            <td>3</td>
            <td>4</td>
            <td>5</td>
            <td>6</td>
            <td>7</td>
            <td>8</td>
            <td>9</td>
            <td>10</td>
            <td>11</td>
            <td>12</td>
            <td>13</td>
            <td>14</td>
            <td>15</td>
            <td>16</td>
            <td>17</td>
            <td>18</td>
            <td>19</td>
            <td>20</td>
            <td>21</td>
            <td>22</td>
            <td>23</td>
            <td>24</td>
        </tr>
        <tr>
            <th>Base 25</th>
            <td>C</td>
            <td>M</td>
            <td>7</td>
            <td>W</td>
            <td>D</td>
            <td>6</td>
            <td>N</td>
            <td>4</td>
            <td>R</td>
            <td>H</td>
            <td>F</td>
            <td>9</td>
            <td>Z</td>
            <td>L</td>
            <td>3</td>
            <td>X</td>
            <td>K</td>
            <td>Q</td>
            <td>G</td>
            <td>V</td>
            <td>P</td>
            <td>B</td>
            <td>T</td>
            <td>J</td>
            <td>Y</td>
        </tr>
    </tbody>
</table>

## References

* A non-exhaustive list of store IDs is included (stores.tsv). You can also find store IDs by inspecting the return data from the [McDonald's restaurant locator](https://www.mcdonalds.com/gb/en-gb/restaurant-locator.html) or by simply checking receipts.
* Discussion on Reverse Engineering Stack Exchange where this was originally posted: https://reverseengineering.stackexchange.com/questions/32129/mcdonalds-receipt-codes
