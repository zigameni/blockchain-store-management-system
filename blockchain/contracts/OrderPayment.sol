// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

/**
 * @title OrderPayment
 * @dev A smart contract for managing order payments with escrow functionality.
 * The contract holds funds until delivery is confirmed, then distributes them
 * between the owner (80%) and courier (20%).
 */

contract OrderPayment {
    address payable public owner_address;
    address payable public courier_address;
    address public customer_address;

    uint public order_price;
    bool public paid;
    bool public delivered;

    // Events for tracking important state changes on the blockchain
    event PaymentReceived(address indexed customer, uint amount);
    event CourierAssigned(address indexed courier);
    event DeliveryConfirmed(address indexed customer);
    event FundsDistributed(address indexed owner, uint ownerAmount, address indexed courier, uint courierAmount);

    constructor(
        address payable _owner_address,
        address payable _courier_address,
        address _customer_address,
        uint _order_price
    ){
        owner_address = _owner_address;
        courier_address = _courier_address;
        customer_address = _customer_address;
        order_price = _order_price;
        paid = false;                          // Order starts as unpaid
        delivered = false;                     // Order starts as undelivered
    }

    /**
     * @dev Allows the customer to pay for the order
     * The funds are held in escrow by the contract until delivery is confirmed
     * Requirements:
     * - Caller must be the customer
     * - Payment amount must exactly match the order price
     * - Order must not already be paid
     */
    function pay() external payable {
        require(msg.sender == customer_address, "Only customer can pay!");
        require(msg.value == order_price, "Incorrect payment amount!");
        require(!paid, "Order already paid!");

        paid = true;                           // Mark order as paid
        emit PaymentReceived(msg.sender, msg.value);  // Emit event for tracking
    }

    /**
     * @dev Allows the owner to assign or reassign a courier to the order
     * This provides flexibility if the original courier becomes unavailable
     * @param _courier_address Address of the courier to assign
     * Requirements:
     * - Caller must be the owner
     * - Order must be paid first
     * - Either no courier is assigned yet, or reassigning to the same courier
     */
    function assignCourier(address payable _courier_address) external {
        require(msg.sender == owner_address, "Only owner can assign courier!");
        require(paid, "Order must be paid first!");
        require(courier_address == address(0) || courier_address == _courier_address, "Courier already assigned!");

        courier_address = _courier_address;    // Set or update the courier address
        emit CourierAssigned(_courier_address);
    }

    /**
     * @dev Allows the customer to confirm delivery, triggering payment distribution
     * This is the critical function that releases funds from escrow
     * The payment is split: 80% to owner, 20% to courier
     * Requirements:
     * - Caller must be the customer
     * - Order must be paid
     * - A courier must be assigned
     * - Delivery must not already be confirmed
     */
    function confirmDelivery() external {
        require(msg.sender == customer_address, "Only customer can confirm delivery!");
        require(paid, "Order must be paid!");
        require(courier_address != address(0), "Courier must be assigned!");
        require(!delivered, "Order already delivered!");

        delivered = true;                      // Mark order as delivered

        // Calculate payment split: 80% to owner, 20% to courier
        uint owner_amount = (order_price * 80) / 100;
        uint courier_amount = order_price - owner_amount;  // Ensures all funds are distributed

        // Transfer funds from contract to respective parties
        owner_address.transfer(owner_amount);
        courier_address.transfer(courier_amount);

        // Emit events for tracking the delivery and fund distribution
        emit DeliveryConfirmed(msg.sender);
        emit FundsDistributed(owner_address, owner_amount, courier_address, courier_amount);
    }

    // View functions (read-only, don't modify state, no gas cost when called externally)

    /**
     * @dev Returns whether the order has been paid
     * @return bool indicating payment status
     */
    function isPaid() external view returns (bool) {
        return paid;
    }

    /**
     * @dev Returns whether the order has been delivered
     * @return bool indicating delivery status
     */
    function isDelivered() external view returns (bool) {
        return delivered;
    }

    /**
     * @dev Returns the current balance held by the contract
     * Should be equal to order_price after payment and 0 after delivery
     * @return uint contract balance in wei
     */
    function getContractBalance() external view returns (uint) {
        return address(this).balance;
    }

}
